import pandas as pd

from itertools import groupby
from django.http import JsonResponse

import threading
import time

from stockapp.tools import progress_bar

from stockapp.crawler import wantgoo_crawler

import chromedriver_autoinstaller
from selenium import webdriver  
from bs4 import BeautifulSoup
import json
from pandas import json_normalize

def CountContinuous(df):
    pd.options.mode.chained_assignment = None

    count = 0
    df[df < 0] = -1
    df[df > 0] = 1
    groups = groupby(df.values.tolist())
    grouped_elements = [list(group) for key, group in groups]
    
    if grouped_elements[0][0] == 1:
        count = len(grouped_elements[0])
    elif grouped_elements[0][0] == -1:
        count = -len(grouped_elements[0])
    else:
        count = 0
        
    return count

def read_institutional_investors(request, code, end_date):
    data = []
    
    try:
        df = pd.read_csv(f'djangoapp/stockapp/files/institutional-investors/{code}.csv')
        df = df[df['date'] <= end_date]
        df = df.reset_index()
        df = df[df.index < 20]
        df = df.drop(columns=['index'])
        i = 0
        while i < len(df.index):
            temp = {
                'date': df['date'][i],
                'sumING': str(df['sumING'][i]),
                'sumForeign': str(df['sumForeign'][i]),
                'sumDealer': str(df['sumDealer'][i])
            }
            data.append(temp)
            
            i += 1
    except:
        pass
    
    return JsonResponse(data, safe=False)

def count_read_institutional_investors(request, code, end_date):
    data = []
    
    try:
        df = pd.read_csv(f'djangoapp/stockapp/files/institutional-investors/{code}.csv')
        df = df[df['date'] <= end_date]
        df = df.reset_index()
        df = df[df.index < 20]
        df = df.drop(columns=['index'])
        data.append({
            'sumForeign': CountContinuous(df['sumForeign']),
            'sumING': CountContinuous(df['sumING']),
            'sumDealer': CountContinuous(df['sumDealer']),
        })
    except:
        pass
    
    return JsonResponse(data, safe=False)
import winsound

def sync():
    stock_list = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')['代碼'].values.tolist()

    chromedriver_autoinstaller.install(cwd=True)

    chrome_options = webdriver.ChromeOptions() 
    
    driver_institutional_investors = webdriver.Chrome(options=chrome_options)
    driver_institutional_investors.minimize_window()
    driver_institutional_investors.implicitly_wait(5)

    driver_historical_daily_candlesticks = webdriver.Chrome(options=chrome_options)
    driver_historical_daily_candlesticks.minimize_window()
    driver_historical_daily_candlesticks.implicitly_wait(5)
    
    threads = []

    print("三大法人買賣超")
    threads.append(threading.Thread(target =  wantgoo_crawler.sync_institutional_investors, args = (stock_list, driver_institutional_investors, )))
    threads[0].start()
    
    print("趨勢分析")
    threads.append(threading.Thread(target =  wantgoo_crawler.sync_historical_daily_candlesticks, args = (stock_list, driver_historical_daily_candlesticks, )))
    threads[1].start()
    
    for i in range(len(threads)):
        threads[i].join()

    winsound.Beep(500,500)
    print("同步完成")

    return True