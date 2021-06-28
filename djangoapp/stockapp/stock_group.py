from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from stockapp.models import *

import pandas as pd

from stockapp.crawler import wantgoo_crawler

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
    
    stock_group = stock_group_list.get(id = group_id)
    title = '股票群組'
    
    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')
    stock_df['代碼名稱'] = stock_df['代碼'].astype(str) + ' ' + stock_df['商品']
    default_stock_list = stock_df['代碼名稱'].values.tolist()

    stock_group_item_list = StockGroupItem.objects.filter(
        StockGroup = stock_group
    )

    daily_candlestick = wantgoo_crawler.crawler_daily_candlestick(2330)
    print(daily_candlestick)
    
    eps_data = wantgoo_crawler.crawler_eps_data(2330)
    print(eps_data[0])

    monthly_revenue_data = wantgoo_crawler.crawler_monthly_revenue_data(2330)
    print(monthly_revenue_data[0])

    if request.method == "POST":
        print("")

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

        StockGroupItem.objects.get_or_create(
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