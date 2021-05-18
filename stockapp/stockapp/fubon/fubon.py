# -*- coding: utf-8 -*-
import requests
from .fubon_list import *
from bs4 import BeautifulSoup

class Branch:
	def __init__(self, id, name):
		self.id = id
		self.name = name

def get_branch(name):
	for item in g_BrokerList.split(';'):
		if item.find(name) != -1:
			broker_id = item.split(',')[0]
			for i in item.split(',')[2:]:
				if i.find(name) != -1:
					branch_id = i.split('!')[1]
	
	return [broker_id, branch_id]

def get_id_name(broker_id):
	find_index = g_BrokerList.find(broker_id) + len(broker_id) + 1
	find_colon_index = g_BrokerList[find_index:].find(';')
	find_exclamation_index = g_BrokerList[find_index:].find('!')

	if find_colon_index != -1 and find_colon_index < find_exclamation_index:
		return Branch(broker_id, g_BrokerList[find_index : find_index + find_colon_index])
	else:
		return Branch(broker_id, g_BrokerList[find_index : find_index + find_exclamation_index])

class Stock:
	def __init__(self, array, branch):
		try:
			self.id = array[0].split(',')[0][2:]
			self.name = array[0].split(',')[1]
		except:
			self.id = array[0][0:5]
			self.name = array[0][5:]
		self.buy_in = int(array[1].replace(',', ''))
		self.sell_out = int(array[2].replace(',', ''))
		self.diff = int(array[3].replace(',', ''))
		self.branch = [branch]
	
	def __lt__(self, other):
		return self.diff < other.diff

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

	for item in broker_branch:
		fubon_list = fubon_crawler(item[0], item[1], begin_date, end_date)
		for fubon in fubon_list:
			id = split_name(fubon[0])[0]
			name = split_name(fubon[0])[1]
			buy_in = int(fubon[1].replace(',', ''))
			sell_out = int(fubon[2].replace(',', ''))
			diff = int(fubon[3].replace(',', ''))
			test = {
				'id': id,
				'name': name,
				'diff': diff,
				'branch': [get_id_name(item[1]).name + ": " + str(diff)],
			}
			if test['diff'] >= 0:
				stock_list['positive'].append(test)
			else:
				stock_list['negative'].append(test)
	
	stock_list['positive'] = custom_sort_list(stock_list['positive'])
	stock_list['negative'] = custom_sort_list(stock_list['negative'])
	
	stock_list = merge_list(stock_list)

	stock_list['positive'].sort(key=lambda k: (k.get('diff', 0)), reverse=True)
	stock_list['negative'].sort(key=lambda k: (k.get('diff', 0)))

	return stock_list

def merge_list(stock_list):
	data = {'positive':[], 'negative':[]}

	for positive in stock_list['positive']:
		temp = {
			'id': None,
			'name': None,
			'diff': None,
			'buy_in': "",
			'sell_out': "",
		}
		for negative in stock_list['negative']:
			if positive['id'] == negative['id']:
				temp['id'] = positive['id']
				temp['name'] = positive['name']
				temp['diff'] = positive['diff'] + negative['diff']
				temp['buy_in'] = positive['branch']
				temp['sell_out'] = negative['branch']
				
				if temp['diff'] > 0:
					data['positive'].append(temp)
				else:
					data['negative'].append(temp)
				
				positive['id'] = None
				negative['id'] = None
				break
	
	for positive in stock_list['positive']:
		if positive['id'] != None:
			temp = {
				'id': positive['id'],
				'name': positive['name'],
				'diff': positive['diff'],
				'buy_in': positive['branch'],
				'sell_out': None,
			}
			data['positive'].append(temp)
	
	for negative in stock_list['negative']:
		if negative['id'] != None:
			temp = {
				'id': negative['id'],
				'name': negative['name'],
				'diff': negative['diff'],
				'buy_in': None,
				'sell_out': negative['branch'],
			}
			data['negative'].append(temp)
	
	return data

def custom_sort_list(to_do_list):
	for i in range(len(to_do_list)):
		for j in range(i + 1, len(to_do_list)):
			try:
				if to_do_list[i]['id'] == to_do_list[j]['id']:
					to_do_list[i]['branch'].append(to_do_list[j]['branch'][0])
					to_do_list[i]['diff'] += to_do_list[j]['diff']
					del to_do_list[j]
			except:
				pass
	
	return to_do_list

def fubon_crawler(broker, branch, begin_date, end_date):
	url = "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm?a=" + broker + "&b=" + branch + "&c=B&e=" + begin_date + "&f=" + end_date
	resource_page = requests.get(url)

	soup = BeautifulSoup(resource_page.text, "html.parser")

	stock_name = soup.find_all('td', class_="t4t1")
	stock_price = soup.find_all('td', class_="t3n1")

	index_name = 0
	index_price = 0

	stock_list = []
	try:
		while index_name < len(stock_name):
			tmp_list= []
			try:
				first_index = stock_name[index_name].script.string.find('\'')
				last_index = stock_name[index_name].script.string.rfind('\'') + 1
				tmp_list.append(stock_name[index_name].script.string[first_index:last_index].replace('\'', ''))
			except:
				tmp_list.append(stock_name[index_name].a.string)
				
			cnt = 0
			while cnt < 3:
				tmp_list.append(stock_price[index_price].string)
				index_price += 1
				cnt += 1
			index_name += 1
			stock_list.append(tmp_list.copy())
	except:
		pass
	
	return stock_list