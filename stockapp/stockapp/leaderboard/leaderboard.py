from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..wantgoo.institutional_investors import *

from ..load_csv import *

class Stock:
    def __init__(self, code, name, diff):
        self.code = code
        self.name = name
        self.diff = diff
        self.date = []
        self.days = None
        self.sumForeign = None
        self.sumING = None
        self.sumDealer = None
        self.capital = None
        self.industry = None
        self.status = None
    
    def __lt__(self, other):
        return self.code < other.code

def StockSort(data_list, dict_stock_list, dates):
    data = []
    
    i = 0
    while i < len(data_list):
        stock = Stock(data_list[i].code, data_list[i].name, data_list[i].diff)
        stock.date.append(data_list[i].date[0])
        j = i + 1
        while j < len(data_list) and data_list[i].code == data_list[j].code:
            stock.diff += data_list[j].diff
            stock.date.append(data_list[j].date[0])
            j += 1
        stock.date.sort(reverse=True)

        if len(stock.code) == 4:
            stock_data = read_csv('stockapp/csv/' + stock.code + '.csv', stock.date[0])
            count = continuous(stock_data[1:])
            stock.sumForeign = count['sumForeign']
            stock.sumING = count['sumING']
            stock.sumDealer = count['sumDealer']
            for dict_stock in dict_stock_list:
                if stock.code == dict_stock['代碼']:
                    stock.capital = dict_stock['股本']
                    stock.industry = dict_stock['產業']
                    stock.status = dict_stock['產業地位']
                    break
        day = 0
        while day < len(stock.date) and stock.date[day] == dates[day]:
            day += 1
        stock.days = day
        data.append(stock)

        i = j

    return data

@login_required
def index(request):
    User = request.user
    title = "排行榜"
    leader_list = []
    buyin_list = []
    sellout_list = []
    buyin_date = []
    sellout_date = []
    
    for file in request.FILES.getlist('uploadfiles'):
        file_date = file.name.split(' ')[-1][:-4]
        if file.name.split(' ')[1] == '買入':
            buyin_date.append(file_date)
        else:
            sellout_date.append(file_date)
        decoded_file = file.read().decode('utf-8-sig').replace('\t', '').splitlines()
        csv_data = csv.DictReader(decoded_file)
        
        for data in csv_data:
            code = data['股票代碼']
            name = data['名稱']
            diff = int(data['差額(仟元)'].replace(',', ''))
            stock = Stock(code, name, diff)
            stock.date.append(file_date)
            if stock.diff > 0:
                buyin_list.append(stock)
            else:
                sellout_list.append(stock)
    
    buyin_date.sort(reverse=True)
    sellout_date.sort(reverse=True)
    buyin_list.sort()
    sellout_list.sort()
    
    dict_stock_list = load_dict_stock_list()

    buyin_list = StockSort(buyin_list, dict_stock_list, buyin_date)
    sellout_list = StockSort(sellout_list, dict_stock_list, sellout_date)
    
    return render(request, 'leaderboard.html', locals())