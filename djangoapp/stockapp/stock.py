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

from bokeh.plotting import figure
from bokeh.embed import components

from bokeh.plotting import figure

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models import Legend

from bokeh.palettes import Dark2

from bokeh.models import Legend

from bokeh.palettes import Spectral4, Dark2
from bokeh.models import ColumnDataSource, BoxAnnotation
from bokeh.models import RangeSlider
from bokeh.layouts import layout, row, Spacer

from bokeh.models.callbacks import CustomJS

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

    title = f'股票'
    today = date.today().strftime("%Y-%m-%d")
    begin_date = today
    end_date = today
    
    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')
    stock_df['代碼名稱'] = stock_df['代碼'].astype(str) + ' ' + stock_df['商品']
    default_stock_list = stock_df['代碼名稱'].values.tolist()
    for i in range(len(default_stock_list)):
        if default_stock_list[i][:4] == str(code):
            full_code_name = default_stock_list[i]
            title = f'{full_code_name}'
            break
    
    stock_list = models.StockModel.objects.filter(
        Owner = User
    )
    get_stock = models.StockModel.objects.filter(
        Code = code
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

    df = pd.read_csv(f'djangoapp/stockapp/files/historical-daily-candlesticks/{code}.csv')
    df = df[::-1].reset_index()
    df = df.drop(columns=['index'])
    df.columns  = ['date', 'open', 'high', 'low', 'close', 'volume']
    df['date']  = pd.to_datetime(df['date'])
    df['MA5']   = df['close'].rolling(5).mean()
    df['MA10']  = df['close'].rolling(10).mean()
    df['MA20']  = df['close'].rolling(20).mean()
    df['MA60']  = df['close'].rolling(60).mean()
    df['MA120'] = df['close'].rolling(120).mean()
    df['MA240'] = df['close'].rolling(240).mean()
    inc = df.close > df.open
    dec = df.open > df.close

    date_length = 60
    x_end = len(df)
    x_start = x_end - date_length
    y_start = df['close'][-date_length:].min() * 0.95
    y_end = df['close'][-date_length:].max() * 1.05
    
    plot_width = 1545
    
    hover = HoverTool(
        tooltips=[
            ('date'   , '@date{%F}'),
            ('open'   , '@open'), 
            ('high'   , '@high'),
            ('low'    , '@low'),
            ('close'  , '@close'),
            ('volume' , '@volume')
        ],
        formatters = {
            '@date' : 'datetime',
            'open'  : 'numeral',
            'high'  : 'numeral',
            'low'   : 'numeral',
            'close' : 'numeral',
        },
        mode='vline'
    )
    p1 = figure(
        title = f'{full_code_name} K線圖',
        tools = [hover, 'save'],
        x_range = (x_start, x_end),
        y_range = (y_start, y_end),
        plot_width = plot_width,
        toolbar_location = 'above'
    )
    p1.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(df['date']))
    }

    df_source = ColumnDataSource(df)
    inc_data = df[inc]
    dec_data = df[dec]
    inc_source = ColumnDataSource(inc_data)
    dec_source = ColumnDataSource(dec_data)
    p1.segment(
        'index',
        'high',
        'index',
        'low',
        color = 'black',
        source = df_source
    )
    vbar1 = p1.vbar(
        'index',
        0.5,
        'open',
        'close',
        fill_color = '#eb2409',
        line_color = 'black',
        source= inc_source
    )
    vbar2 = p1.vbar(
        'index',
        0.5,
        'open',
        'close',
        fill_color = '#00995c',
        line_color = 'black',
        source = dec_source
    )
    p1.hover.renderers = [vbar1, vbar2]

    ma_legend_items = []
    for ma_name, color in zip(['MA5', 'MA10', 'MA20', 'MA60', 'MA120', 'MA240'], Dark2[6]):
        ma_df = df[['date', 'close', 'open', 'high', 'low', 'volume', ma_name]]
        
        source = ColumnDataSource(ma_df)
        ma_line = p1.line(
            x = 'index',
            y = ma_name,
            line_width = 2,
            color = color,
            alpha = 0.8,
            muted_color = color,
            muted_alpha = 0.2,
            source = source
        )
        ma_legend_items.append((ma_name, [ma_line]))
    legend = Legend(
        items = ma_legend_items,
        location = (50, 50)
    )
    p1.add_layout(legend)

    p2 = figure(
        x_range = (0, x_end),
        y_range = (df['close'].min(), df['close'].max()),
        plot_width = plot_width,
        plot_height = 100,
        toolbar_location = None
    )
    p2.xaxis.major_label_overrides = {
        i: date.strftime('%Y-%m-%d') for i, date in enumerate(pd.to_datetime(df["date"]))
    }
    p2.line(
        x='index',
        y='close',
        line_width=2,
        color="black",
        alpha=0.8,
        source=df_source
    )
    p2.yaxis.major_label_text_color = None
    p2.yaxis.major_tick_line_color= None
    p2.yaxis.minor_tick_line_color= None
    p2.grid.grid_line_color=None

    box = BoxAnnotation(
        fill_alpha = 0.5,
        line_alpha = 0.5,
        level = 'underlay',
        left = x_start,
        right = x_end
    )
    p2.add_layout(box)

    range_slider = RangeSlider(
        title = None,
        start = 0,
        end = x_end,
        value = (x_start, x_end),
        default_size = plot_width-30,
        step = 1
    )
    range_slider.js_link('value', p1.x_range, 'start', attr_selector=0)
    range_slider.js_link('value', p1.x_range, 'end', attr_selector=1)
    range_slider.js_link('value', box, 'left', attr_selector=0)
    range_slider.js_link('value', box, 'right', attr_selector=1)
    
    callback = CustomJS(
        args = dict(
            xr = p1.x_range,
            yr = p1.y_range,
            data = source.data
        ),
        code =
            """
                let begin = Math.floor(xr.start);
                let end = Math.floor(xr.end);
                let array = data.close.slice(begin, end);
                
                let y_start = Math.min(...array) * 0.95;
                let y_end = Math.max(...array) * 1.05;
                
                yr.start = y_start;
                yr.end = y_end;
            """
        )
    p1.x_range.js_on_change('start', callback)
    
    stock_layout = layout(
        [
            [p1],
            [p2],
            row(Spacer(width=20),range_slider)
        ]
    )
    
    script, div = components(stock_layout)

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