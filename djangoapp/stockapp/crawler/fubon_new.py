import pandas as pd

from itertools import groupby
from django.http import JsonResponse

import threading
import time

from stockapp.tools import progress_bar

from stockapp.crawler import fubon_crawler

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

def sync_institutional_investors():
    stock_list = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')['代碼'].values.tolist()
    
    start = time.time()
    
    institutional_investors_data = []
    threads_number = 50
    i = 0
    while i < len(stock_list):
        threads = []
        j = 0
        while j < threads_number and i + j < len(stock_list):
            progress_bar("爬蟲中: ", i + j + 1, len(stock_list))
            threads.append(threading.Thread(target = fubon_crawler.crawler_institutional_investors, args = (institutional_investors_data, stock_list[i + j], )))
            threads[j].start()
            j += 1
        
        for j in range(len(threads)):
            threads[j].join()
        
        i += threads_number
    end = time.time()
    min = int((end - start) / 60)
    sec = int((end - start) % 60)
    print(f"\n爬蟲時間: {min}分:{sec}秒")

    start = time.time()
    with pd.HDFStore('djangoapp/stockapp/files/institutional-investors.h5',  mode='w') as store:
        i = 0
        while i < len(institutional_investors_data):
            code = institutional_investors_data[i]['code']
            code_name = f'code{code}'
            institutional_investors_data[i]['df'].to_csv(f'djangoapp/stockapp/files/institutional-investors/{code}.csv', index = 0)
            store.append(code_name, institutional_investors_data[i]['df'],  data_columns=['date'], format='table')
            
            progress_bar("存檔中: ", i + 1, len(stock_list))
            i += 1

    end = time.time()
    print(f"\n存檔時間: {int(end - start)}秒")

    return True

def sync_historical_daily_candlesticks():
    stock_list = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')['代碼'].values.tolist()
    
    start = time.time()
    
    historical_daily_candlesticks_data = []
    threads_number = 50
    i = 0
    while i < len(stock_list):
        threads = []
        j = 0
        while j < threads_number and i + j < len(stock_list):
            progress_bar("爬蟲中: ", i + j + 1, len(stock_list))
            threads.append(threading.Thread(target = fubon_crawler.crawler_historical_daily_candlesticks, args = (historical_daily_candlesticks_data, stock_list[i + j], )))
            threads[j].start()
            j += 1
        
        for j in range(len(threads)):
            threads[j].join()
        
        time.sleep(1)
        
        i += threads_number

    end = time.time()
    min = int((end - start) / 60)
    sec = int((end - start) % 60)
    print(f"\n爬蟲時間: {min}分:{sec}秒")

    start = time.time()
    with pd.HDFStore('djangoapp/stockapp/files/historical-daily-candlesticks.h5',  mode='w') as store:
        i = 0
        while i < len(historical_daily_candlesticks_data):
            code = historical_daily_candlesticks_data[i]['code']
            code_name = f'code{code}'
            historical_daily_candlesticks_data[i]['df'].to_csv(f'djangoapp/stockapp/files/historical-daily-candlesticks/{code}.csv', index = 0)
            store.append(code_name, historical_daily_candlesticks_data[i]['df'],  data_columns=['date'], format='table')
            
            progress_bar("存檔中: ", i + 1, len(stock_list))
            i += 1

    end = time.time()
    print(f"\n存檔時間: {int(end - start)}秒")

    return True