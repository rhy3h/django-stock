from pandas import json_normalize
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import date, datetime, timedelta
import time

def sync_institutional_investors(stock_list, driver):
    institutional_investors_data = []

    i = 0
    while i < len(stock_list):
        code = stock_list[i]
        try:
            driver.get(f"https://www.wantgoo.com/stock/{code}/institutional-investors/trend")
            driver.get(f"https://www.wantgoo.com/stock/{code}/institutional-investors/trend-data?topdays=20")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            dict_from_json = json.loads(soup.find("body").text)
            df = json_normalize(dict_from_json)

            df['date'] = df['date'].str[:10]
            df['sumForeign'] = df['sumForeignWithDealer'] + df['sumForeignNoDealer']
            df = df.drop(columns=['sumForeignWithDealer', 'sumForeignNoDealer'])
            df['sumDealer'] = df['sumDealerBySelf'] + df['sumDealerHedging']
            df = df.drop(columns=['sumDealerBySelf', 'sumDealerHedging'])
            df = df.drop(columns=['investrueId', 'foreignHolding', 'ingHolding', 'dealerHolding', 'foreignHoldingRate', 'sumHoldingRate'])

            institutional_investors_data.append({
                'code': code,
                'df': df
            })
        except:
            i -= 1
        i += 1

    driver.quit()

    with pd.HDFStore('djangoapp/stockapp/files/institutional-investors.h5',  mode='w') as store:
        i = 0
        while i < len(institutional_investors_data):
            code = institutional_investors_data[i]['code']
            code_name = f'code{code}'
            institutional_investors_data[i]['df'].to_csv(f'djangoapp/stockapp/files/institutional-investors/{code}.csv', index = 0)
            store.append(code_name, institutional_investors_data[i]['df'],  data_columns=['date'], format='table')
            i += 1

    return True

def sync_historical_daily_candlesticks(stock_list, driver):
    tomorrow = date.today() + timedelta(days = 1)
    tomorrow_string = tomorrow.strftime("%Y-%m-%d")
    tomorrow_timestamp = int(time.mktime(datetime.strptime(tomorrow_string, "%Y-%m-%d").timetuple()) * 1000)
    
    historical_daily_candlesticks_data = []

    i = 0
    while i < len(stock_list):
        code = stock_list[i]
        try:
            driver.get(f"https://www.wantgoo.com/stock/{code}/technical-chart")
            driver.get(f"https://www.wantgoo.com/investrue/{code}/historical-daily-candlesticks?before={tomorrow_timestamp}&top=240")
            soup = BeautifulSoup(driver.page_source, "html.parser")

            dict_from_json = json.loads(soup.find("body").text)
            df = json_normalize(dict_from_json)

            df = df.drop(columns=['tradeDate'])
            df['time'] = df['time'].add(28800000)
            df['time'] = df['time'].floordiv(1000)

            historical_daily_candlesticks_data.append({
                'code': code,
                'df': df
            })

        except:
            i -= 1
        
        i += 1
    
    driver.quit()
    
    with pd.HDFStore('djangoapp/stockapp/files/historical-daily-candlesticks.h5',  mode='w') as store:
        i = 0
        while i < len(historical_daily_candlesticks_data):
            code = historical_daily_candlesticks_data[i]['code']
            code_name = f'code{code}'
            historical_daily_candlesticks_data[i]['df'].to_csv(f'djangoapp/stockapp/files/historical-daily-candlesticks/{code}.csv', index = 0)
            store.append(code_name, historical_daily_candlesticks_data[i]['df'],  data_columns=['date'], format='table')
            i += 1
        
    return True