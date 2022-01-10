from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from stockapp.crawler.fubon import read_institutional_investors, read_historical_daily_candlesticks

from stockapp.crawler.moneydj_crawler import crawler_trading_volume, crawler_listed_trading_amount, crawler_intersection

from datetime import date

import pandas as pd

@login_required
def trading_volume(request):
    User = request.user
    title = "市場面之成交量選股法"

    rank_list = crawler_trading_volume()

    return render(request, 'trading-volume.html', locals())

@login_required
def trading_amount(request):
    User = request.user
    title = "值大排行"

    # 0 是 上市
    # 1 是 上櫃
    if request.method == "POST":
        type = request.POST.get('type')
        days = request.POST.get('days')
    
        rank_list = crawler_listed_trading_amount(type, days)

    return render(request, 'trading-amount.html', locals())

@login_required
def base(request):
    User = request.user
    title = "交集"
    
    columns = ['代碼', '股票', '量增率', '成交量(張)', '五日均量(張)', '成交值(千元)', '外資', '投信', '自營商', '股本', '產業', '產業地位','收盤價','漲跌幅(%)','5日(%)','10日(%)','20日(%)','60日(%)','120日(%)','240日(%)']
    
    # 0 是 上市
    # 1 是 上櫃
    rank_list = []
    if request.method == "POST":
        type = request.POST.get('type')
        days = request.POST.get('days')
        set = request.POST.get('set')
        
        if set == "intersection":
            rank_list = crawler_intersection(type, days)
        
        end_date = date.today().strftime('%Y-%m-%d')

        stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')

        try:
            with pd.HDFStore('djangoapp/stockapp/files/institutional-investors.h5', mode='r') as newstore:
                for stock in rank_list:
                    df = stock_df[stock_df['代碼'] == int(stock.code)]
                    
                    if not df.empty:
                        stock.capital = df['股本'].values[0]
                        stock.industry = df['產業'].values[0]
                        stock.status = df['產業地位'].values[0]
                    try:
                        df_restored = newstore.select('code' + stock.code)
                        read_institutional_investors(df_restored, stock, end_date)
                    except:
                        pass
        except:
            pass 
        try:
            with pd.HDFStore('djangoapp/stockapp/files/historical-daily-candlesticks.h5', mode='r') as newstore:
                for stock in rank_list:
                    try:
                        df_restored = newstore.select('code' + stock.code)
                        read_historical_daily_candlesticks(df_restored, stock)
                    except:
                        pass
        except:
            pass

    return render(request, 'rank.html', locals())