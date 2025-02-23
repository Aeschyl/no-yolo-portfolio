import requests
import json
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# implement value at risk using Covariance/Montecarlo simulation

from dotenv import load_dotenv
import os

load_dotenv()

fmp_key = os.getenv("FMP_KEY")

rand = random.randint(0, len(api_keys) - 1)

# Get today's date
today = datetime.today()

# Loop through the last 12 months
def calculate_change_arr_year(symbol):
    data = []
    for i in range(12):
        # Calculate the first day of the month
        first_day = (today - relativedelta(months=i)).replace(day=1)
        
        # Adjust the date if it falls on a weekend or is January 1st
        while first_day.weekday() >= 5 or (first_day.month == 1 and first_day.day == 1) or (first_day.month == 9 and first_day.day == 2):
            first_day += timedelta(days=1)
        
        first_day_str = first_day.strftime('%Y-%m-%d')
        
        # Make the API call for the adjusted first day of the month
        url = f'https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}/?apikey={fmp_key}&from={first_day_str}&to={first_day_str}'
        response = requests.get(url)
        historical_data = response.json().get('historical', [])
        print(response.json())
        if historical_data:
            open_price = historical_data[0].get('open')
            close_price = historical_data[0].get('close')
        else:
            open_price = close_price = None

        data.append((open_price, close_price))
        
    # Calculate the change using a sliding window
    changes = []
    for i in range(0, len(data) - 1):
        finalprice = (data[i][0] + data[i][1]) / 2
        startprice = (data[i+1][0] + data[i+1][1]) / 2
        
        change = ((finalprice - startprice) / startprice) * 100
        print("changesddsds" + str(change))
        changes.append(change)
        
    return changes


