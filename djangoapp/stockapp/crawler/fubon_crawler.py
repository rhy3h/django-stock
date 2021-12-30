from pandas import json_normalize
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import date, datetime, timedelta
import time
import requests

def crawler_institutional_investors(institutional_investors_data, code):
    while True:
        url = f"https://fubon-ebrokerdj.fbs.com.tw/Z/ZC/ZCL/CZCL3.DJBCD?A={code}&B=Y"
        resource_page = requests.get(url)

        if resource_page.status_code == 200:
            try:
                data = resource_page.text.split(' ')

                date = data[0].split(',')
                sumForeign = data[5].split(',')
                sumING = data[6].split(',')
                sumDealer = data[7].split(',')
                
                date.reverse()
                sumForeign.reverse()
                sumING.reverse()
                sumDealer.reverse()
                
                for i in range(len(date)):
                    month = date[i][:2]
                    day = date[i][2:]
                    date[i] = f"{month}-{day}"

                stock = {
                    "date": date, 
                    "sumForeign": [int(i) for i in sumForeign],
                    "sumING": [int(i) for i in sumING],
                    "sumDealer": [int(i) for i in sumDealer],
                }
                df = pd.DataFrame(stock)

                institutional_investors_data.append({
                    'code': code,
                    'df': df
                })
                break
            except:
                break
        else:
            time.sleep(3)
    return True

import time
# 趨勢分析
def crawler_historical_daily_candlesticks(historical_daily_candlesticks_data, code):
    while True:
        url = f"https://fubon-ebrokerdj.fbs.com.tw/z/BCD/czkc1.djbcd?a={code}&b=D&c=2880&E=1&ver=5"
        resource_page = requests.get(url)

        if resource_page.status_code == 200:
            try:
                data = resource_page.text.split(' ')

                date = data[0].split(',')
                open = data[1].split(',')
                high = data[2].split(',')
                low = data[3].split(',')
                close = data[4].split(',')
                volume = data[5].split(',')

                date.reverse()
                open.reverse()
                high.reverse()
                low.reverse()
                close.reverse()
                volume.reverse()

                stock = {
                    "date": date, 
                    "open": [float(i) for i in open],
                    "high": [float(i) for i in high],
                    "low": [float(i) for i in low],
                    "close": [float(i) for i in close],
                    "volume": [float(i) for i in volume]
                }
                df = pd.DataFrame(stock)
            
                historical_daily_candlesticks_data.append({
                    'code': code,
                    'df': df
                })
                break
            except:
                break
        else:
            time.sleep(3)
    return True