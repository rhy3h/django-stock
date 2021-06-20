import requests
import csv
import os
from .apis import api

def read_csv(file, end_date):
    data = [['date', 'sumForeign', 'sumING', 'sumDealer']]
    count = 0
    with open(file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if count > 20:
                break
            if end_date[5:] >= row[0]:
                data.append(row)
                count += 1
    return data

def institutional_investors_data(stock_id):
    data = []
    
    url = "https://www.wantgoo.com/stock/" + stock_id + "/institutional-investors/trend-data?topdays=90"

    resource_page = api(url)
    
    for item in resource_page:
        temp = {}
        sumForeign = item['sumForeignWithDealer'] + item['sumForeignNoDealer']
        sumING = item['sumING']
        sumDealer = item['sumDealerBySelf'] + item['sumDealerHedging']
        
        temp['date'] = item['date'][5:10]
        temp['sumForeign'] = sumForeign
        temp['sumING'] = sumING
        temp['sumDealer'] = sumDealer
        data.append(temp)
        
    return data

def continuous(stock_data):
    data = {
        'sumForeign': None,
        'sumING': None,
        'sumDealer': None
    }

    positiveForeign = -1
    positiveING = -1
    positiveDealer = -1
    negativeForeign = -1
    negativeING = -1
    negativeDealer = -1
    
    if len(stock_data) < 10:
        return data
    count = 0
    for stock in stock_data:
        sumForeign = int(stock[1])
        sumING = int(stock[2])
        sumDealer = int(stock[3])

        if positiveForeign == -1 and sumForeign <= 0:
            positiveForeign = count
        if negativeForeign == -1 and sumForeign >= 0:
            negativeForeign = count
        
        if positiveING == -1 and sumING <= 0:
            positiveING = count
        if negativeING == -1 and sumING >= 0:
            negativeING = count
        
        if positiveDealer == -1 and sumDealer <= 0:
            positiveDealer = count
        if negativeDealer == -1 and sumDealer >= 0:
            negativeDealer = count
        
        count += 1
    
    if positiveForeign > negativeForeign:
        data['sumForeign'] = positiveForeign
    else:
        data['sumForeign'] = -negativeForeign
    if data['sumForeign'] == 0 and int(stock_data[0][1]) != 0:
        data['sumForeign'] = 10
    
    if positiveING > negativeING:
        data['sumING'] = positiveING
    else:
        data['sumING'] = -negativeING
    if data['sumING'] == 0 and int(stock_data[0][2]) != 0:
        data['sumING'] = 10
    
    if positiveDealer > negativeDealer:
        data['sumDealer'] = positiveDealer
    else:
        data['sumDealer'] = -negativeDealer
    if data['sumDealer'] == 0 and int(stock_data[0][3]) != 0:
        data['sumDealer'] = 10
    
    return data

from ..load_csv import *

def stock_append_data(item, end_date):
    stock_code = item.code
    
    if len(stock_code) == 5:
        return item
    try:
        dict_stock_list = load_dict_stock_list()

        stock_data = read_csv('stockapp/csv/' + stock_code + '.csv', end_date)
        count = continuous(stock_data[1:])
        item.sumForeign = count['sumForeign']
        item.sumING = count['sumING']
        item.sumDealer = count['sumDealer']
        for stock in dict_stock_list:
            if stock_code == stock['代碼']:
                item.capital = stock['股本']
                item.industry = stock['產業']
                item.status = stock['產業地位']
                break
    except:
        pass
    
    return item