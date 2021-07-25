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

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA

import backtesting

class SmaCross(Strategy):
    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, 5)
        self.sma2 = self.I(SMA, close, 10)
    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

def test(request):
    backtesting.set_bokeh_output(notebook=False)
    df = pd.read_csv('djangoapp/stockapp/files/historical-daily-candlesticks/2330.csv')
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'QuoteVolume']
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    df.set_index('Date', inplace=True)
    
    bt = Backtest(df, SmaCross,
                cash=10000, commission=.002,
                exclusive_orders=True)

    output = bt.run()
    bt.plot()

    return redirect('/stock-group/')