from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..wantgoo.institutional_investors import institutional_investors_data, stock_append_data

import csv

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

@login_required
def index(request):
    User = request.user
    title = "排行榜"
    leader_buyin_list = []
    leader_sellout_list = []
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
                flag_index = -1
                for item in leader_buyin_list:
                    if item.code == stock.code:
                        flag_index = int(leader_buyin_list.index(item))
                        break
                if flag_index > -1:
                    leader_buyin_list[flag_index].diff += stock.diff
                    leader_buyin_list[flag_index].date.append(file_date)
                else:
                    leader_buyin_list.append(stock)
            else:
                flag_index = -1
                for item in leader_sellout_list:
                    if item.code == stock.code:
                        flag_index = int(leader_sellout_list.index(item))
                
                if flag_index > -1:
                    leader_sellout_list[flag_index].diff += stock.diff
                    leader_sellout_list[flag_index].date.append(file_date)
                else:
                    leader_sellout_list.append(stock)
    
    buyin_date.reverse()
    sellout_date.reverse()
    
    i = 0
    while i < len(leader_buyin_list):
        leader_buyin_list[i].date.reverse()
        day = 0
        while day < len(leader_buyin_list[i].date) and leader_buyin_list[i].date[day] == buyin_date[day]:
            day += 1
        leader_buyin_list[i].days = day
        if day == 0:
            leader_buyin_list.remove(leader_buyin_list[i])
            i -= 1
        stock_append_data(leader_buyin_list[i], leader_buyin_list[i].date[0])
        i += 1
    
    i = 0
    while i < len(leader_sellout_list):
        leader_sellout_list[i].date.reverse()
        day = 0
        while day < len(leader_sellout_list[i].date) and leader_sellout_list[i].date[day] == sellout_date[day]:
            day += 1
        leader_sellout_list[i].days = day
        if day == 0:
            leader_sellout_list.remove(leader_sellout_list[i])
            i -= 1
        stock_append_data(leader_sellout_list[i], leader_sellout_list[i].date[0])
        i += 1
    
    return render(request, 'leaderboard/index.html', locals())