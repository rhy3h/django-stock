import requests
from pandas import json_normalize
import pandas as pd

# 三大法人買賣超
def crawler_institutional_investors(institutional_investors_data, code):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'f-none-match': 'W/"0E388198B4C3285D182724181C442790"'
    }

    url = f"https://www.wantgoo.com/stock/{code}/institutional-investors/trend-data?topdays=90"
    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'

    data = resource_page.json()
    df = json_normalize(data)
    
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
    return True

# 趨勢分析
def crawler_historical_daily_candlesticks(historical_daily_candlesticks_data, code, today_timestamp):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'f-none-match': 'W/"6065B067AEAD258E41F585B1793F254A"'
    }

    url = f"https://www.wantgoo.com/investrue/{code}/historical-daily-candlesticks?before={today_timestamp}&top=240"
    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    data = resource_page.json()
    df = json_normalize(data)

    df = df.drop(columns=['tradeDate'])
    df['time'] = df['time'].add(28800000)
    df['time'] = df['time'].floordiv(1000)    
    
    historical_daily_candlesticks_data.append({
        'code': code,
        'df': df
    })
    return True

# 收盤價，當日漲跌幅
def crawler_daily_candlestick(code):
    data = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }
    
    url = f"https://www.wantgoo.com/investrue/{code}/daily-candlestick"
    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    data = resource_page.json()
    
    return data

# 每股盈餘
def crawler_eps_data(code):
    data = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }
    
    url = f"https://www.wantgoo.com/stock/{code}/financial-statements/eps-data"
    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    data = resource_page.json()
    
    return data

# 每月營收
def crawler_monthly_revenue_data(code):
    data = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }
    
    url = f"https://www.wantgoo.com/stock/{code}/financial-statements/monthly-revenue-data"
    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    data = resource_page.json()
    
    return data

# 本益比
def crawler_price_earning_ratio(code):
    data = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }
    
    url = f"https://www.wantgoo.com/stock/{code}/enterprise-value/data"
    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    data = resource_page.json()
    
    return data
