import pandas as pd
import requests
from pandas import json_normalize
import math

from itertools import groupby
from django.http import JsonResponse
from datetime import datetime

import threading
import time

def progress_bar(count, length, last_time):
    print("[%-25s] %d/%d (%d%%) 預估剩餘時間: %d:%d" % ('='*(int)(count / length * 25), count, length, (count / length * 100), math.floor(last_time / 60), math.floor(last_time % 60)), end='\r')

def crawler_institutional_investors(code):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    url = f"https://www.wantgoo.com/stock/{code}/institutional-investors/trend-data?topdays=90"
    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    data = resource_page.json()
    df = json_normalize(data)
    
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['sumForeign'] = df['sumForeignWithDealer'] + df['sumForeignNoDealer']
    df = df.drop(columns=['sumForeignWithDealer', 'sumForeignNoDealer'])
    df['sumDealer'] = df['sumDealerBySelf'] + df['sumDealerHedging']
    df = df.drop(columns=['sumDealerBySelf', 'sumDealerHedging'])
    df = df.drop(columns=['investrueId', 'foreignHolding', 'ingHolding', 'dealerHolding', 'foreignHoldingRate', 'sumHoldingRate'])

    writer = pd.ExcelWriter(f'djangoapp/stockapp/files/xlsx/{code}.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    
    return True

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
        df = pd.read_excel(f'djangoapp/stockapp/files/xlsx/{code}.xlsx')
        df = df[df['date'] <= end_date]
        df = df.reset_index()
        df = df[df.index < 20]
        df = df.drop(columns=['index'])
        
        i = 0
        while i < len(df.index):
            temp = {
                'date': df['date'][i].strftime("%Y-%m-%d"),
                'sumING': str(df['sumING'][i]),
                'sumForeign': str(df['sumForeign'][i]),
                'sumDealer': str(df['sumDealer'][i])
            }
            data.append(temp)
            
            i += 1

        sumING = CountContinuous(df['sumING'])
        sumForeign = CountContinuous(df['sumForeign'])
        sumDealer = CountContinuous(df['sumDealer'])
    except:
        pass
    
    return JsonResponse(data, safe=False)

def count_read_institutional_investors(request, code, end_date):
    data = []

    try:
        df = pd.read_excel(f'djangoapp/stockapp/files/xlsx/{code}.xlsx')
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

    path = 'djangoapp/stockapp/files/xlsx/'
    
    start = time.time()
    
    estimate = 3
    threads_number = 50
    last_time = (len(stock_list) / threads_number) * estimate
    i = 0
    while i < len(stock_list):
        progress_bar(int(i / threads_number), int(len(stock_list) / threads_number), last_time)
        threads = []
        j = 0
        while j < threads_number and i + j < len(stock_list):
            threads.append(threading.Thread(target = crawler_institutional_investors, args = (stock_list[i + j],)))
            threads[j].start()
            j += 1
        
        for j in range(threads):
            threads[j].join()
        
        last_time -= estimate
        i += threads_number
    
    end = time.time()
    
    min = int((end - start) / 60)
    sec = int((end - start) % 60)
    print(f"\n爬蟲時間: {min}分:{sec}秒")

    return True