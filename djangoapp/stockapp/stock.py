from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from stockapp import models

import pandas as pd

from datetime import date, datetime, timedelta

from stockapp.crawler import esun

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA

from django.http import HttpResponse, JsonResponse

from django.utils.encoding import escape_uri_path

import backtesting

@login_required
def base(request):
    User = request.user
    title = '股票'
    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')
    stock_df['代碼名稱'] = stock_df['代碼'].astype(str) + ' ' + stock_df['商品']
    default_stock_list = stock_df['代碼名稱'].values.tolist()
    
    stock_list = models.StockModel.objects.filter(
        Owner = User
    )

    if request.POST.get('search'):
        return redirect(f'/stock/2330')
    else:
        return render(request, 'stock.html', locals())

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

@login_required
def index(request, code):
    User = request.user

    title = '股票'
    today = date.today().strftime("%Y-%m-%d")
    begin_date = today
    end_date = today
    
    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')
    stock_df['代碼名稱'] = stock_df['代碼'].astype(str) + ' ' + stock_df['商品']
    default_stock_list = stock_df['代碼名稱'].values.tolist()
    for i in range(len(default_stock_list)):
        if default_stock_list[i][:4] == str(code):
            full_code_name = default_stock_list[i]
            break
    stock_list = models.StockModel.objects.filter(
        Owner = User
    )
    
    if request.POST.get('search'):
        begin_date = request.POST.get('begin-date')
        begin_datatime = datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = request.POST.get('end-date')
        end_datatime = datetime.strptime(end_date, "%Y-%m-%d")

        if end_datatime.isoweekday() > 5:
            end_date = (end_datatime + timedelta(days = (5 - end_datatime.isoweekday()))).strftime("%Y-%m-%d")
        if begin_datatime.isoweekday() > 5:
            begin_date = (begin_datatime + timedelta(days = (5 - begin_datatime.isoweekday()))).strftime("%Y-%m-%d")

        if begin_date > end_date:
            begin_date, end_date = end_date, begin_date
        
        begin_date_split = begin_date.split('-')
        new_begin_date = f"{begin_date_split[0]}-{int(begin_date_split[1])}-{int(begin_date_split[2])}"
        end_date_split = end_date.split('-')
        new_end_date = f"{end_date_split[0]}-{int(end_date_split[1])}-{int(end_date_split[2])}"

        broker_table = esun.crawler(code, new_begin_date, new_end_date)

    return render(request, 'stock.html', locals())

def add(request, code):
    User = request.user
    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')
    stock_df['代碼名稱'] = stock_df['代碼'].astype(str) + ' ' + stock_df['商品']
    default_stock_list = stock_df['代碼名稱'].values.tolist()
    for i in range(len(default_stock_list)):
        if default_stock_list[i][:4] == str(code):
            name = default_stock_list[i][5:]
            break
    
    models.StockModel.objects.get_or_create(
        Owner = User,
        Code = code,
        Name = name
    )
    return redirect('/stock/' + str(code))

def delete(request, code):
    return redirect('/stock/' + str(code))

def backtesting(request, code):
    try:
        df = pd.read_csv(f'djangoapp/stockapp/files/historical-daily-candlesticks/{code}.csv')
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'QuoteVolume']
        df['Date'] = pd.to_datetime(df['Date'], unit='s')
        df.set_index('Date', inplace=True)
        bt = Backtest(df, SmaCross, cash = 10000, commission = .002, exclusive_orders = True)
        output = bt.run()
        bt.plot(filename = f"djangoapp/stockapp/files/backtest_result/{code}.html", open_browser = False)

        file = open(f'djangoapp/stockapp/files/backtest_result/{code}.html', 'rb')
        response = HttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment;filename="{code}.html"'

        return response
    except:
        pass