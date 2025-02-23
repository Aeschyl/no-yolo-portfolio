import pandas as pd
import numpy as np
import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import time
from datetime import datetime, timedelta
import random
import statistics
from fmp import calculate_change_arr_year
from ollama import chat
from ollama import ChatResponse

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

def load_and_merge_data():
    """Loads and merges market cap and sector data."""
    market_cap_df = pd.read_csv(market_cap_file, usecols=['Symbol', 'Marketcap'])
    sector_df = pd.read_csv(sector_file, usecols=['Ticker', 'Sector'])
    df = pd.merge(market_cap_df, sector_df, left_on='Symbol', right_on='Ticker')
    df['Marketcap'] = pd.to_numeric(df['Marketcap'], errors='coerce')
    df.drop(columns=['Ticker'], inplace=True)
    return df

def get_least_heavy_sectors(df):
    """Analyzes the user's portfolio and identifies underrepresented sectors."""
    userInput = pd.read_csv(user_input_file, usecols=['Symbol'])
    userShi = df[df['Symbol'].isin(userInput['Symbol'])]
    all_industry = dict.fromkeys(df['Sector'].unique(), 0)
    user_industry_counts = userShi['Sector'].value_counts()
    for sector, count in user_industry_counts.items():
        all_industry[sector] = count
    least_heavy_sectors = sorted(all_industry, key=all_industry.get)[:5]
    return least_heavy_sectors

def save_recommendations(recommendations):
    """Saves the recommendations to a CSV file with additional information."""
    df = pd.read_csv('sp500_companies.csv')
    recommendations_df = df[df['Symbol'].isin(recommendations[1])][['Symbol', 'Longname', 'Sector', 'Longbusinesssummary']]
    recommendations_df = pd.merge(recommendations, recommendations_df, left_on=1, right_on='Symbol')
    recommendations_df.drop(columns=[1], inplace=True)
    recommendations_df = recommendations_df.rename(columns={0: 'UserSymbol'})
    recommendations_df = recommendations_df.rename(columns={2: 'cov'})
    recommendations_df.to_csv(output_file, index=False)
    print(f"Stock recommendations saved to {output_file}")

    
def generate_covariance(symbol, least_heavy_sectors, symbol_changes):
    """Generates and compares covariance data for the passed in symbol."""
    
    # prestored symbols with monthly changes
    symbol_changes_file = './symbol_changes.csv'
    symbol_changes_df = pd.read_csv(symbol_changes_file)
        
    print(least_heavy_sectors[0])
    
    symb_changes = np.array(symbol_changes)

    correlations = []
    
    b = 0
    j = 0
    print(symbol_changes_df.iterrows())
    for row in symbol_changes_df.iterrows():
        b += 1
        if row[1][1] in least_heavy_sectors[0]:
            j += 1
            curr = []
            for i in range(2, 13):
                curr.append(row[1][i])
            correlation = np.corrcoef(symb_changes, np.array(curr))
            correlations.append((symbol, row[1][0], abs(correlation[0][1]), ))
    print("b", b)
    print("j", j)
    print(least_heavy_sectors[0])
    correlations = sorted(correlations, key=lambda x: x[2]) 
    return pd.DataFrame(correlations[:5])


def generate_defense(user_symbol, cov, symbol, user_symbol_changes, symbol_changes):
    messages = [
        {
            'role': 'user',
            'content': f'''You have to generate well-founded and quantitative reasoning for why this stock is a good diversification strategy for the user's portfolio. Your task is to construct a well-reasoned argument explaining why these stocks are fundamentally unrelated and why investing in Symbol could enhance portfolio diversification and how this can benefit the user. Don't just skim over why diversification is beneficial, think why it's beneficial in this specific scenario based on the given values before answering. 
                            I'm giving you the following data - User's portoflio symbol: {user_symbol}, Correlation coefficient: {cov}, Uncorrelated symbol: {symbol}, Monthly percent changes to the user's symbol over past year: {user_symbol_changes}, Monthly percent changes to the recommended symbol over past year from Jan 2025 back to Feb 2024 : {symbol_changes}  The cov stands for the result of running the UserSymbol and Symbol through, and a value closer to 0 as the result of a covariance matrix shows that stocks aren't closely related. 
                            I want you to structure a reason for why these stocks are unrelated and why someone should consider investing in the symbol we recommend to diversify their portfolio. Consider factors like financial metrics, information you have about the company's industries, performance, ESG performance, goals, geographic presence, the greeks, etc. Don't just provide a summary of what the company does. Your response should be a single, cohesive paragraph that presents a data-backed argument without explicitly stating "invest in X instead of Y." Instead, emphasize the benefits of diversification, illustrating how adding Symbol can improve risk-adjusted returns and portfolio stability. Use concrete statistics and relevant comparisons to support your reasoning. Ensure that your response is tailored to the specific data provided and is not simply stating that the stocks are in different sectors or have different market caps.
                        '''
        }
    ]

    # Call the chat function to get the response
    response: ChatResponse = chat(model='qwen:0.5b', messages=messages)

    # Access and print the content of the response
    return response.message.content


market_cap_file = './sp500_companies.csv'
sector_file = './sp500-with-gics.csv'
user_input_file = './userData.csv'
output_file = './recommendations.csv'

def recommend_stocks():
    """Main function to orchestrate the recommendation process."""
    df = load_and_merge_data()
    least_heavy_sectors = get_least_heavy_sectors(df)
    
    userTickers = pd.read_csv(user_input_file, usecols=['Symbol'])
    userTickersWSectors = df[df['Symbol'].isin(userTickers['Symbol'])]
    recommendations = pd.DataFrame(columns=[0, 1, 2])
    changes = {}
    for symbol in userTickersWSectors['Symbol']:
        symbol_changes = calculate_change_arr_year(symbol)
        changes[symbol] = symbol_changes
        recommendation = generate_covariance(symbol, least_heavy_sectors, symbol_changes)
        recommendations = pd.concat([recommendations, recommendation], ignore_index=True)
    print(recommendations)
    
    """

    symbol_changes = pd.read_csv('symbol_changes.csv') 

    for symbol in userTickersWSectors['Symbol']:
        for row in recommendations.iterrows():
            #print(row)
            user_symbol = row[1][0]
            symbol = row[1][1]
            print("symbmb", symbol)
            cov = row[1][2]
            #print("cov", cov)
            symbol_row = symbol_changes[symbol_changes['Symbol'] == symbol].iloc[0]
            print(symbol_row)
            symbol_changes_array = []
            for i in range(2, 13):
                symbol_changes_array.append(float(symbol_row[i]))
            print(symbol_changes_array)
        
            #llm_shizz = generate_defense(user_symbol, cov, symbol, changes.get(symbol), symbol_changes)
            #print("shizzz", llm_shizz)
            
    """
    
    save_recommendations(recommendations)



recommend_stocks()