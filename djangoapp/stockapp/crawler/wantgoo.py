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

import time, random
from atpbar import atpbar

from atpbar import flush
import threading
import os

def sync():
    stock_list = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')['代碼'].values.tolist()

    chromedriver_autoinstaller.install(cwd=True)

    chrome_options_0 = webdriver.ChromeOptions()
    os.system('start chrome --remote-debugging-port=5500')
    chrome_options_0.add_experimental_option("debuggerAddress", "127.0.0.1:5500")
    driver = webdriver.Chrome(options=chrome_options_0)
    driver.minimize_window()
    driver.implicitly_wait(1)
    
    threads = []

    print("三大法人買賣超")
    threads.append(threading.Thread(target =  wantgoo_crawler.sync_institutional_investors, args = (stock_list, driver, )))
    threads[0].start()
    
    for i in range(len(threads)):
        threads[i].join()
        
    print("趨勢分析")
    threads.append(threading.Thread(target =  wantgoo_crawler.sync_historical_daily_candlesticks, args = (stock_list, driver, )))
    threads[1].start()
    
    for i in range(len(threads)):
        threads[i].join()

    print("同步完成")

    return True