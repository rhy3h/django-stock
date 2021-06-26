# -*- coding: utf-8 -*-
import requests
from stockapp.crawler.list import g_BrokerList
from bs4 import BeautifulSoup

import pandas as pd
import threading
from stockapp.crawler.wantgoo import CountContinuous

import time

from stockapp.tools import progress_bar

class FubonStock:
    def __init__(self, code, name, diff, broker, branch):
        self.code = code
        self.name = name
        self.diff = diff
        self.broker = broker
        self.branch = branch
    
    def __lt__(self, other):
        return self.code < other.code

class Branch:
    def __init__(self, id, name, diff):
        self.id = id
        self.name = name
        self.diff = diff
    
    def __lt__(self, other):
        return self.diff > other.diff

class StockClass:
    def __init__(self, code, name, diff):
        self.code = code
        self.name = name
        self.diff = diff
        self.buyin = []
        self.sellout = []
        self.sumForeign = None
        self.sumING = None
        self.sumDealer = None
        self.capital = None
        self.industry = None
        self.status = None

def crawler(crawler_set_list, broker, branch, begin_date, end_date):
    url = "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=" + broker + "&b=" + branch + "&c=B&e=" + begin_date + "&f=" + end_date
    resource_page = requests.get(url)

    soup = BeautifulSoup(resource_page.text, "html.parser")

    stock_name = soup.find_all('td', class_="t4t1")
    stock_price = soup.find_all('td', class_="t3n1")

    crawler_list = []
    
    i = 0
    while i < len(stock_name):
        try:
            first_index = stock_name[i].script.string.find('\'')
            last_index = stock_name[i].script.string.rfind('\'') + 1
            code_name = stock_name[i].script.string[first_index:last_index].replace('\'', '')
            code = code_name.split(',')[0][2:]
            name = code_name.split(',')[1]
            diff = int(stock_price[i * 3 + 2].string.string.replace(',', ''))
            fubon_stock = FubonStock(code, name, diff, broker, branch)
            crawler_list.append(fubon_stock)
        except:
            pass
        i += 1
    
    for item in crawler_list:
        crawler_set_list.append(item)

def NameToID(name):
    BrokerList = []
    for item in g_BrokerList.split(';'):
        BrokerList.append(item.split('!'))

    if name.find('-') > -1:
        broker_name = name.split('-')[0]
    else:
        broker_name = name

    i = 0
    while i < len(BrokerList):
        broker_id_name = BrokerList[i][0].split(',')
        if broker_id_name[1].find(broker_name) > -1:
            broker_id = broker_id_name[0]
            j = 1
            while j < len(BrokerList[i]):
                branch_id_name = BrokerList[i][j].split(',')
                if branch_id_name[1].find(name) > -1:
                    branch_id = branch_id_name[0]
                    break
                j += 1
            break
        i += 1

    return {'broker_id': broker_id, 'branch_id':  branch_id}

def IDToName(broker, branch):
    BrokerList = []
    for item in g_BrokerList.split(';'):
        BrokerList.append(item.split('!'))
    
    i = 0
    while i < len(BrokerList):
        broker_id_name = BrokerList[i][0].split(',')
        if broker_id_name[0] == broker:
            j = 1
            while j < len(BrokerList[i]):
                branch_id_name = BrokerList[i][j].split(',')
                if branch_id_name[0] == branch:
                    branch_name = branch_id_name[1]
                    break
                j += 1
            break
        i += 1
    
    return {'branch_name': branch_name}

def read_xlsx_append_data(df, stock, end_date):
    try:
        df = df[df['date'] <= end_date]
        df = df.reset_index()
        df = df[df.index < 20]
        
        stock.sumING = CountContinuous(df['sumING'])
        stock.sumForeign = CountContinuous(df['sumForeign'])
        stock.sumDealer = CountContinuous(df['sumDealer'])
    except:
        pass

def CrawlerList(broker_branch, begin_date, end_date):
    stock_table = {'positive':[], 'negative':[]}

    BrokerList = []
    for item in g_BrokerList.split(';'):
        BrokerList.append(item.split('!'))
    
    start = time.time()

    threads = []
    crawler_set_list = []
    i = 0
    while i < len(broker_branch):
        threads.append(threading.Thread(target = crawler, args = (crawler_set_list, broker_branch[i].broker_code, broker_branch[i].branch_code, begin_date, end_date,)))
        threads[i].start()
        progress_bar("爬蟲中: ", i + 1, len(broker_branch))
        i += 1
    for i in range(len(threads)):
        threads[i].join()

    end = time.time()
    print(f"\n爬蟲時間: {round(end - start, 2)} 秒")

    start = time.time()

    crawler_set_list.sort()

    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')

    i = 0
    while i < len(crawler_set_list):
        stock = StockClass(crawler_set_list[i].code, crawler_set_list[i].name, crawler_set_list[i].diff)

        branch_i_name = IDToName(crawler_set_list[i].broker, crawler_set_list[i].branch)['branch_name']
        branch_i = Branch(crawler_set_list[i].broker, branch_i_name, crawler_set_list[i].diff)
        if crawler_set_list[i].diff > 0:
            stock.buyin.append(branch_i)
        else:
            stock.sellout.append(branch_i)

        j = i + 1
        while j < len(crawler_set_list) and crawler_set_list[i].code == crawler_set_list[j].code:
            branch_j_name = IDToName(crawler_set_list[j].broker, crawler_set_list[j].branch)['branch_name']
            branch_j = Branch(crawler_set_list[j].branch, branch_j_name, crawler_set_list[j].diff)
            if crawler_set_list[j].diff > 0:
                stock.buyin.append(branch_j)
            else:
                stock.sellout.append(branch_j)
            
            stock.diff += crawler_set_list[j].diff
            j += 1

        stock.buyin.sort()
        stock.sellout.sort(reverse=True)
        
        df = stock_df[stock_df['代碼'] == int(stock.code)]
        
        if not df.empty:
            stock.capital = df['股本'].values[0]
            stock.industry = df['產業'].values[0]
            stock.status = df['產業地位'].values[0]
        
        if stock.diff > 0:
            stock_table['positive'].append(stock)
        else:
            stock_table['negative'].append(stock)
        i = j
    
    with pd.HDFStore('djangoapp/stockapp/files/institutional-investors.h5',  mode='r') as newstore:
        count = 1
        i = 0
        while i < len(stock_table['positive']):
            try:
                df_restored = newstore.select('code' + stock_table['positive'][i].code)
                read_xlsx_append_data(df_restored, stock_table['positive'][i], end_date)
            except:
                pass
            
            progress_bar("彙整中: ", count, len(stock_table['positive']) + len(stock_table['negative']))
            count += 1
            i += 1
        
        i = 0
        while i < len(stock_table['negative']):
            try:
                df_restored = newstore.select('code' + stock_table['negative'][i].code)
                read_xlsx_append_data(df_restored, stock_table['negative'][i], end_date)
            except:
                pass

            progress_bar("彙整中: ", count, len(stock_table['positive']) + len(stock_table['negative']))
            count += 1

            i += 1
    
    end = time.time()
    print(f"\n彙整時間: {round(end - start, 2)} 秒")

    return stock_table