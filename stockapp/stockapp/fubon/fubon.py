# -*- coding: utf-8 -*-
import requests
from .fubon_list import *
from bs4 import BeautifulSoup

class Branch:
    def __init__(self, id, name, diff):
        self.id = id
        self.name = name
        self.diff = diff
    

def get_branch(name):
    for item in g_BrokerList.split(';'):
        if item.find(name) > -1:
            broker_id = item.split('!')[0].split(',')[0]
            for branch in item.split('!')[1:]:
                if branch.find(name) > -1:
                    branch_id = branch.split(',')[0]
            break
    
    return [broker_id, branch_id]

def get_id_name(broker_id, diff):
    find_index = g_BrokerList.find(broker_id) + len(broker_id) + 1
    find_colon_index = g_BrokerList[find_index:].find(';')
    find_exclamation_index = g_BrokerList[find_index:].find('!')

    if find_colon_index != -1 and find_colon_index < find_exclamation_index:
        return Branch(broker_id, g_BrokerList[find_index : find_index + find_colon_index], diff)
    else:
        return Branch(broker_id, g_BrokerList[find_index : find_index + find_exclamation_index], diff)

def split_name(array):
    try:
        id = array.split(',')[0][2:]
        name = array.split(',')[1]
    except:
        id = array[0:5]
        name = array[5:]
    return [id, name]

def fubon_get_list(broker_branch, begin_date, end_date):
    stock_list = {'positive':[], 'negative':[]}
    
    for branch in broker_branch:
        broker_id = branch[0]
        branch_id = branch[1]
        fubon_list = fubon_crawler(broker_id, branch_id, begin_date, end_date)
        for data in fubon_list:
            temp = {
                '股票代碼': data['股票代碼'],
                '股票名稱': data['股票名稱'],
                '差額': data['差額'],
                '券商分部': get_id_name(branch_id, data['差額'])
            }
            if temp['差額'] >= 0:
                stock_list['positive'].append(temp)
            else:
                stock_list['negative'].append(temp)
    
    stock_list = merge_list(stock_list)
    
    return stock_list

class Stock:
    def __init__(self, code, name, diff):
        self.code = code
        self.name = name
        self.diff = diff
        self.buyin = []
        self.sellout = []
        self.sumForeign = None
        self.sumING = None
        self.sumDealer = None

def merge_list(stock_list):
    data = {'positive':[], 'negative':[]}
    
    for i in range(len(stock_list['positive'])):
        if stock_list['positive'][i] != None:
            stock_code = stock_list['positive'][i]['股票代碼']
            stock_name = stock_list['positive'][i]['股票名稱']
            diff = stock_list['positive'][i]['差額']
            temp = Stock(stock_code, stock_name, diff)
            temp.buyin.append(stock_list['positive'][i]['券商分部'])

            for j in range(len(stock_list['negative'])):
                try:
                    if stock_list['positive'][i]['股票代碼'] == stock_list['negative'][j]['股票代碼']:
                        temp.diff += stock_list['negative'][j]['差額']
                        temp.sellout.append(stock_list['negative'][j]['券商分部'])
                        stock_list['negative'][j] = None
                except:
                    pass
            for k in range(i + 1, len(stock_list['positive'])):
                try:
                    if stock_list['positive'][i]['股票代碼'] == stock_list['positive'][k]['股票代碼']:
                        temp.diff += stock_list['positive'][k]['差額']
                        temp.buyin.append(stock_list['positive'][k]['券商分部'])
                        stock_list['positive'][k] = None
                except:
                    pass
            stock_list['positive'][i] = None
        
            if temp.diff > 0:
                data['positive'].append(temp)
            else:
                data['negative'].append(temp)
    
    for i in range(len(stock_list['negative'])):
        if stock_list['negative'][i] != None:
            stock_code = stock_list['negative'][i]['股票代碼']
            stock_name = stock_list['negative'][i]['股票名稱']
            diff = stock_list['negative'][i]['差額']
            temp = Stock(stock_code, stock_name, diff)
            temp.sellout.append(stock_list['negative'][i]['券商分部'])
            for j in range(i + 1, len(stock_list['negative'])):
                if stock_list['negative'][j] != None:
                    if stock_list['negative'][i]['股票代碼'] == stock_list['negative'][j]['股票代碼']:
                        temp.diff += stock_list['negative'][j]['差額']
                        temp.sellout.append(stock_list['negative'][j]['券商分部'])
                        stock_list['negative'][j] = None
            
            data['negative'].append(temp)
            stock_list['negative'][i] = None
    
    for positive in data['positive']:
        positive.buyin.sort(key=lambda k: (k.diff, 0), reverse=True)
        positive.sellout.sort(key=lambda k: (k.diff, 0))
    
    for negative in data['negative']:
        negative.buyin.sort(key=lambda k: (k.diff, 0), reverse=True)
        negative.sellout.sort(key=lambda k: (k.diff, 0))
    
    return data

def fubon_crawler(broker, branch, begin_date, end_date):
    url = "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=" + broker + "&b=" + branch + "&c=B&e=" + begin_date + "&f=" + end_date
    resource_page = requests.get(url)

    soup = BeautifulSoup(resource_page.text, "html.parser")

    stock_name = soup.find_all('td', class_="t4t1")
    stock_price = soup.find_all('td', class_="t3n1")

    stock_list = []
    
    try:
        for i in range(len(stock_name)):
            first_index = stock_name[i].script.string.find('\'')
            last_index = stock_name[i].script.string.rfind('\'') + 1
            code_name = stock_name[i].script.string[first_index:last_index].replace('\'', '')
            temp = {
                '股票代碼': None,
                '股票名稱': None,
                '買進金額': None,
                '賣出金額': None,
                '差額' : None
            }
            try:
                first_index = stock_name[i].script.string.find('\'')
                last_index = stock_name[i].script.string.rfind('\'') + 1
                code_name = stock_name[i].script.string[first_index:last_index].replace('\'', '')
                temp['股票代碼'] = code_name.split(',')[0][2:]
                temp['股票名稱'] = code_name.split(',')[1]
            except:
                temp['股票代碼'] = None
                temp['股票名稱'] = stock_name[i].a.string.split(',')[1]
            
            temp['買進金額'] = stock_price[i * 3 + 0].string
            temp['賣出金額'] = stock_price[i * 3 + 1].string
            temp['差額'] = int(stock_price[i * 3 + 2].string.string.replace(',', ''))
            
            stock_list.append(temp)
    except:
        pass
    
    return stock_list