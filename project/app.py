import streamlit as st
import pandas as pd
import os
import time
import requests
from datetime import datetime
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

load_dotenv()

market_data_token = os.getenv("MARKET_DATA_KEY")

# Set the page configuration
st.set_page_config(page_title="no-YOLO portfolio", layout="wide")

# Custom CSS to reduce top margins
st.markdown("""
  <style>
    .block-container {
      padding-top: 1rem;
      padding-bottom: 2rem;
    }
    header {
      visibility: hidden;
    }
    #MainMenu {
      visibility: hidden;
    }
    footer {
      visibility: hidden;
    }
  </style>
""", unsafe_allow_html=True)

# Title of the app
st.title("Upload Your Portfolio")

# Instructions for the user
st.write("""
  Please upload a CSV file containing your portfolio. The CSV file should have a column named 'Symbol' with the stock tickers of the companies in your portfolio.""")
  
# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Cache the stock data fetching function to prevent redundant API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour (3600 seconds)
def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch stock data for a single symbol"""
    try:
        url = f"https://api.marketdata.app/v1/stocks/candles/D/{symbol}?from={start_date}&to={end_date}&token={market_data_token}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('s') == 'ok' and len(data.get('t', [])) > 0:
                df = pd.DataFrame({
                    "Date": [datetime.fromtimestamp(t).strftime('%Y-%m-%d') for t in data['t']],
                    "Open": data['o'],
                    "Close": data['c'],
                    "High": data['h'],
                    "Low": data['l'],
                    "Volume": data['v'],
                    "Symbol": symbol
                })
                df["Moving_Avg"] = df["Close"].rolling(window=7).mean()
                return df
    except Exception as e:
        st.error(f"Error fetching market data for {symbol}: {str(e)}")
    return pd.DataFrame()

def create_stock_plot(combined_df: pd.DataFrame, symbols: list) -> go.Figure:
    """Create a plotly figure for the stock data"""
    fig = go.Figure()
    for symbol in symbols:
        stock_data = combined_df[combined_df["Symbol"] == symbol]
        fig.add_trace(go.Scatter(
            x=stock_data["Date"],
            y=stock_data["Moving_Avg"],
            mode="lines",
            name=f"{symbol} 7-day MA",
            line=dict(width=2),
        ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=True,
        template="plotly_dark",
        hovermode="x unified",
        margin=dict(t=10, b=20),
        height=500
    )
    return fig

# Main app logic
if uploaded_file is not None:
    if 'portfolio_processed' not in st.session_state:
        # Read the uploaded CSV file
        user_portfolio = pd.read_csv(uploaded_file, usecols=['Symbol'])
        temp_file_path = './userData.csv'
        user_portfolio.to_csv(temp_file_path, index=False)
        
        st.session_state.symbols = user_portfolio['Symbol'].tolist()
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Initial portfolio processing
        status_text.text('Processing your portfolio...')
        progress_bar.progress(10)
        time.sleep(0.1)

        # Run the backend script
        status_text.text('Analyzing portfolio composition...')
        progress_bar.progress(25)
        os.system(f'python3 ./recommender.py')
        
        # Read recommendations
        status_text.text('Loading recommendations...')
        progress_bar.progress(40)
        recommendations_df = pd.read_csv('./recommendations.csv')
        
        # Fetch market data
        status_text.text('Fetching market data...')
        progress_bar.progress(60)
        
        if 'stock_data' not in st.session_state:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - pd.Timedelta(days=365)).strftime('%Y-%m-%d')
            
            all_symbols = st.session_state.symbols + recommendations_df['Symbol'].tolist()
            #all_symbols = list(set(all_symbols))  # Remove duplicates
            
            all_data = []
            total_symbols = len(all_symbols)
            for idx, symbol in enumerate(all_symbols):
                status_text.text(f'Fetching data for {symbol}...')
                progress_value = 60 + (idx / total_symbols * 30)
                progress_bar.progress(int(progress_value))
                
                df = fetch_stock_data(symbol, start_date, end_date)
                if not df.empty:
                    all_data.append(df)
            
            if all_data:
                st.session_state.stock_data = pd.concat(all_data, ignore_index=True)
            else:
                st.session_state.stock_data = pd.DataFrame()
        
        status_text.text('Analysis complete!')
        progress_bar.progress(100)
        time.sleep(0.2)
        
        # Clear the progress indicators
        status_text.empty()
        progress_bar.empty()
        
        # Store recommendations in session state
        st.session_state.recommendations_df = recommendations_df
        # Mark as processed
        st.session_state.portfolio_processed = True
    else:
        # Use the stored recommendations
        recommendations_df = st.session_state.recommendations_df

    # Create dropdowns for each portfolio symbol in the sidebar
    with st.sidebar:
      st.title("Select Your Portfolio and Recommendations")

      # Group recommendations by UserSymbol
      grouped_recommendations = recommendations_df.groupby("UserSymbol")["Symbol"].unique().to_dict()
      
      # Create a selectbox for the user to choose a stock from their portfolio
      selected_user_symbol = st.selectbox("Choose one of your stocks to analyze", list(grouped_recommendations.keys()))

      # Create a selectbox for the user to choose a recommendation based on the selected stock
      if selected_user_symbol:
        selected_recommendation = st.selectbox(f"Recommendations for {selected_user_symbol}", grouped_recommendations[selected_user_symbol])

        if selected_recommendation:
          st.session_state.selected_stock = selected_recommendation
          
          
      print(grouped_recommendations)

  # Main content area for displaying stock details
    if 'selected_stock' in st.session_state:
      selected_stock_info = recommendations_df[recommendations_df['Symbol'] == st.session_state.selected_stock].iloc[0]
      st.title(f"Details for {st.session_state.selected_stock}")

      left_column, right_column = st.columns([0.5, 0.5])

      # Left column for text information
      with left_column:
          st.header("Company Information")
          st.write(f"**Long Name:** {selected_stock_info['Longname']}")
          st.write(f"**Sector:** {selected_stock_info['Sector']}")
          st.subheader("Business Summary")
          st.write(selected_stock_info['Longbusinesssummary'])

      with right_column:
          st.markdown("""
              <style>
              [data-testid="stHeader"] {
                  margin-bottom: -3rem;
              }
              </style>
              """, unsafe_allow_html=True)
          st.header("Stock Comparison")
          st.subheader("Demonstrating Lack of Correlation")

          if not st.session_state.stock_data.empty:
              fig = create_stock_plot(st.session_state.stock_data, 
                                      [selected_user_symbol, st.session_state.selected_stock])
              st.plotly_chart(fig, use_container_width=True)
          else:
              st.warning("No data available for selected stocks.")

