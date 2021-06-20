from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ..models import *

from ..load_csv import *

from ..wantgoo.apis import api

@login_required
def base(request):
    User = request.user
    stock_group_list = StockGroup.objects.filter(Owner=User)
    try:
        return redirect('/stock-group/' + str(stock_group_list.first().id))
    except:
        return render(request, 'stock-group.html', locals())

@login_required
def index(request, group_id):
    User = request.user
    stock_group_list = StockGroup.objects.filter(Owner=User)
    broker_group_list = BrokerGroup.objects.filter(Owner=User)
    
    stock_group = stock_group_list.get(id = group_id)
    title = '股票群組'
    default_stock_list = load_list_stock_list()
    stock_list = Stock.objects.filter(
        StockGroup = stock_group
    )
    return render(request, 'stock-group.html', locals())

@login_required
def create(request):
    if request.method == "POST":
        stock_group_list_name = request.POST['stock-group-name']
        User = request.user
        StockGroup.objects.get_or_create(Owner = User,
                                Name = stock_group_list_name)
        stock_group_list = StockGroup.objects.filter(Owner=User).last()

        return redirect('/stock-group/' + str(stock_group_list.id))

@login_required
def add(request, group_id):
    User = request.user
    stock_group = StockGroup.objects.filter(Owner = User).get(id = group_id)

    if request.method == "POST":
        stock_input = request.POST['stock-input']
        code = stock_input.split(' ')[0]
        name = stock_input.split(' ')[1]

        Stock.objects.get_or_create(
            StockGroup = stock_group,
            Code = code,
            Name = name,
        )
    
        return redirect('/stock-group/' + str(group_id))

@login_required
def edit(request, group_id):
    if request.method == "POST":
        new_group_name = request.POST['new-group-name']
        User = request.user
        stock_group_list = StockGroup.objects.get(
            Owner = User,
            id = group_id
        )
        stock_group_list.Name = new_group_name
        stock_group_list.save()
    
    return redirect('/stock-group/' + str(stock_group_list.id))

@login_required
def delete(request, group_id):
    User = request.user
    stock_group_list = StockGroup.objects.get(Owner = User,
                        id = group_id)
    stock_group_list.delete()

    return redirect('/stock-group/')

import datetime

def technical_chart(request, code):
    # User = request.user
    # broker_group_list = Group.objects.filter(Owner=User)
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