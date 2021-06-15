from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ..models import StockGroup

import csv

from ..wantgoo.apis import api

def load_stock_list():
    with open('stockapp/static/js/stock.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stocks = list(reader)
    return stocks

@login_required
def base(request):
    User = request.user
    stock_group = StockGroup.objects.filter(Owner=User)
    title = '股票'

    stocks = load_stock_list()

    return render(request, 'stock/index.html', locals())

@login_required
def index(request, group_id):
    User = request.user
    stock_group = StockGroup.objects.filter(Owner=User)
    group = stock_group.get(id = group_id)
    title = '股票群組'

    return render(request, 'stock/index.html', locals())

@login_required
def create(request):
    if request.method == "POST":
        stock_group_name = request.POST['stock_group_name']
        User = request.user
        StockGroup.objects.get_or_create(Owner = User,
                                Name = stock_group_name)
        stock_group = StockGroup.objects.filter(Owner=User).last()

        return redirect('/stock/' + str(stock_group.id))

import datetime

def technical_chart(request, code):
    # User = request.user
    # group_list = Group.objects.filter(Owner=User)
    # title = '技術分析'

    # today = datetime.date.today()
    # if today.isoweekday() > 5:
    #     today = today + timedelta(days = (5 - today.isoweekday()))
    # today_str = today.strftime("%Y-%m-%d") + ' 00:00:00'
    # today_obj = datetime.datetime.strptime(today_str, '%Y-%m-%d %H:%M:%S')
    # timestamp = (int)(datetime.datetime.timestamp(today_obj))

    # url = 'https://www.wantgoo.com/investrue/%s/historical-daily-candlesticks?before=%d&top=100' % (code, timestamp * 1000)
    # data = api(url)
    
    # for item in data:
    #     item['time'] = datetime.datetime.fromtimestamp((item['time'] / 1000)).strftime("%Y-%m-%d")
    
    # data = list(reversed(data))

    # stocks = load_stock_list()
    # for item in stocks:
    #     if item[0] == code:
    #         code_name = item[1]
    #         break
    
    return render(request, 'stock/technical-chart.html', locals())