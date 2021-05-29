import requests
import csv
import os

def write_csv(file, data):
    with open(file, "a", newline = "") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)
    return data

def read_csv(file):
    data = []
    with open(file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

def institutional_investors_data(stock_id):
    data = []
    
    url = "https://www.wantgoo.com/stock/" + stock_id + "/institutional-investors/trend-data?topdays=10"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    resource_page = requests.get(url,headers = headers)
    resource_page.encoding = 'utf-8'
    
    for item in resource_page.json():
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

def stock_append_data(item, date):
    stock_id = item['id']
    if len(stock_id) == 5:
        return item
    try:
        stock_data = read_csv('stockapp/csv/' + stock_id + '.csv')
        if date == stock_data[1][0]:
            count = continuous(stock_data[1:])
            item['sumForeign'] = count['sumForeign']
            item['sumING'] = count['sumING']
            item['sumDealer'] = count['sumDealer']
        else:
            os.remove('stockapp/csv/' + stock_id + '.csv')
            data = [['date', 'sumForeign', 'sumING', 'sumDealer']]
            for item in institutional_investors_data(stock_id):
                data.append([item['date'], item['sumForeign'], item['sumING'], item['sumDealer']])
            write_csv('stockapp/csv/' + stock_id + '.csv', data)
    except:
        data = [['date', 'sumForeign', 'sumING', 'sumDealer']]
        for item in institutional_investors_data(stock_id):
            data.append([item['date'], item['sumForeign'], item['sumING'], item['sumDealer']])
        write_csv('stockapp/csv/' + stock_id + '.csv', data)
        stock_data = read_csv('stockapp/csv/' + stock_id + '.csv')
        count = continuous(stock_data[1:])
        item['sumForeign'] = count['sumForeign']
        item['sumING'] = count['sumING']
        item['sumDealer'] = count['sumDealer']
    
    return item