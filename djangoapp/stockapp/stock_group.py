from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from stockapp import models

import pandas as pd

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, BoxAnnotation, RangeSlider, Legend
from bokeh.layouts import layout, row, Spacer
from bokeh.models.callbacks import CustomJS

@login_required
def base(request):
    User = request.user
    stock_group_list = models.StockGroup.objects.filter(Owner=User)
    title = '股票群組'
    
    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')
    stock_df['代碼名稱'] = stock_df['代碼'].astype(str) + ' ' + stock_df['商品']
    default_stock_list = stock_df['代碼名稱'].values.tolist()

    try:
        return redirect('/stock-group/' + str(stock_group_list.first().id) + '/?index=0')
    except:
        return render(request, 'stock-group.html', locals())

def generate_graph(code, name):
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
        mode = 'vline'
    )
    p1 = figure(
        title = f'{code} {name} K線圖',
        tools = [hover, 'crosshair, save'],
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
    color = ('#4286F5', '#FEBD09', '#E65596', '#83BF0A', '#834BEB', '#FC7742')
    for ma_name, color in zip(['MA5', 'MA10', 'MA20', 'MA60', 'MA120', 'MA240'], color):
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
        x = 'index',
        y = 'close',
        line_width = 2,
        color = "black",
        alpha = 0.8,
        source = df_source
    )
    p2.toolbar.active_drag = None
    p2.yaxis.major_label_text_color = None
    p2.yaxis.major_tick_line_color = None
    p2.yaxis.minor_tick_line_color = None
    p2.grid.grid_line_color = None

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
            row(
                Spacer(width=20),
                range_slider
            )
        ]
    )
    
    return components(stock_layout)

@login_required
def index(request, group_id):
    User = request.user
    stock_group_list = models.StockGroup.objects.filter(Owner=User)
    
    stock_group = stock_group_list.get(id = group_id)
    title = f'股票群組 {stock_group.Name}'
    
    stock_df = pd.read_excel('djangoapp/stockapp/files/上市、上櫃(股本、產業、產業地位).xlsx')
    stock_df['代碼名稱'] = stock_df['代碼'].astype(str) + ' ' + stock_df['商品']
    default_stock_list = stock_df['代碼名稱'].values.tolist()

    stock_group_item_list = models.StockGroupItem.objects.filter(
        StockGroup = stock_group
    )
    max_length = int(stock_group_item_list.count())
    
    try:
        index = int(request.GET.get('index'))
        code = stock_group_item_list[index].Code
        name = stock_group_item_list[index].Name
        script, div = generate_graph(code, name)
        
        if max_length > 3:
            if index == 0:
                stock_group_item_list = stock_group_item_list[0:3]
            elif index == max_length - 1:
                stock_group_item_list = stock_group_item_list[max_length-3:max_length]
            else:
                stock_group_item_list = stock_group_item_list[index-1:index + 2]
    except:
        pass
            
    return render(request, 'stock-group.html', locals())

@login_required
def create(request):
    if request.method == "POST":
        stock_group_list_name = request.POST['stock-group-name']
        User = request.user
        models.StockGroup.objects.get_or_create(Owner = User,
                                Name = stock_group_list_name)
        stock_group_list = models.StockGroup.objects.filter(Owner=User).last()

        return redirect('/stock-group/' + str(stock_group_list.id))

@login_required
def add(request, group_id):
    User = request.user
    stock_group = models.StockGroup.objects.filter(Owner = User).get(id = group_id)

    if request.method == "POST":
        stock_input = request.POST['stock-input']
        code = stock_input.split(' ')[0]
        name = stock_input.split(' ')[1]

        models.StockGroupItem.objects.get_or_create(
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
        stock_group_list = models.StockGroup.objects.get(
            Owner = User,
            id = group_id
        )
        stock_group_list.Name = new_group_name
        stock_group_list.save()
    
    return redirect('/stock-group/' + str(stock_group_list.id))

@login_required
def delete(request, group_id):
    User = request.user
    stock_group_list = models.StockGroup.objects.get(Owner = User,
                        id = group_id)
    stock_group_list.delete()

    return redirect('/stock-group/')

def upload(request, group_id):
    User = request.user
    stock_group = models.StockGroup.objects.filter(
        Owner = User
    ).get(
        id = group_id
    )
    stock_list = models.StockGroupItem.objects.filter(
        StockGroup = stock_group
    )
    
    if request.method == "POST":
        for broker in stock_list:
            broker.delete()
        
        uploadfile = request.FILES['uploadfile']

        df = pd.read_excel(uploadfile)
        for i in df.index: 
            code = df['代號'][i]
            name = df['名稱'][i]
            models.StockGroupItem.objects.get_or_create(
                StockGroup = stock_group,
                Code = code,
                Name = name,
            )

    return redirect('/stock-group/' + str(group_id) + '/?index=0')

def delete_item(request, group_id, stock_item_id):
    return redirect('/stock-group/' + str(group_id))