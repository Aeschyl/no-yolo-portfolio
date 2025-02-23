import pandas as pd
from fmp import calculate_change_arr_year
import csv

market_cap_df = pd.read_csv('./sp500_companies.csv', usecols=['Symbol', 'Marketcap'])
sector_df = pd.read_csv('./sp500-with-gics.csv', usecols=['Ticker', 'Sector'])
df = pd.merge(market_cap_df, sector_df, left_on='Symbol', right_on='Ticker')
df['Marketcap'] = pd.to_numeric(df['Marketcap'], errors='coerce')
df.drop(columns=['Ticker'], inplace=True)

#df = df.sort_values(by='Marketcap', ascending=False)
top_10_per_sector = df.groupby('Sector').head(10)

"""
with open('symbol_changes.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Symbol', 'Sector', 'January', 'December', 'November', 'October', 'September', 'August', 'July', 'June', 'May', 'April', 'March', 'February'])
"""

for sector, group in top_10_per_sector.groupby('Sector'):
    if sector == 'Communication Services' or sector == 'Consumer Discretionary' or sector == 'Consumer Staples' or sector == 'Energy' or sector == 'Financials' or sector == 'Health Care' or sector == 'Industrials':# or sector == 'Information Technology' or sector == 'Materials' or sector == 'Real Estate' or sector == 'Utilities':
        continue
    for symbol in group['Symbol']:
        ss = calculate_change_arr_year(symbol)
        with open('symbol_changes.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([symbol] + [sector] + ss)