from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

class Stock:
    def __init__(self, code, name, diff):
        self.code = code
        self.name = name
        self.diff = diff
        self.days = 1
        self.date = []

import csv
@login_required
def index(request):
    User = request.user
    title = "排行榜"
    leader_buyin_list = []
    leader_sellout_list = []

    for file in request.FILES.getlist('uploadfiles'):
        file_date = file.name.split(' ')[-1][:-4]

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
                    leader_buyin_list[flag_index].days += 1
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
                    leader_sellout_list[flag_index].days += 1
                    leader_sellout_list[flag_index].date.append(file_date)
                else:
                    leader_sellout_list.append(stock)

    return render(request, 'leaderboard/index.html', locals())