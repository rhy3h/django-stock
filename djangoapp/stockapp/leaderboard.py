from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from django.utils.encoding import escape_uri_path

import pandas as pd

from itertools import groupby

class Stock:
    def __init__(self, code, name, diff):
        self.code = code
        self.name = name
        self.diff = diff
        self.days = None
        self.date = []
        self.sumForeign = None
        self.sumING = None
        self.sumDealer = None
        self.capital = None
        self.industry = None
        self.status = None
        self.five = None
        self.ten = None
        self.twenty = None
        self.sixty = None
        self.one_twenty = None
        self.two_forty = None
        self.close = None
        self.changeRate = None
    
    def __lt__(self, other):
        if self.diff > 0:
            return self.days > other.days or self.days == other.days and self.diff > other.diff
        else:
            return self.days > other.days or self.days == other.days and self.diff < other.diff

def CombineRepeat(dict_list, dates):
    data = []
    
    i = 0
    while i < len(dict_list):
        stock = Stock(dict_list[i]['代碼'], dict_list[i]['股票'], dict_list[i]['差額(仟元)'])
        stock.date.append(dict_list[i]['日期'])
        stock.sumForeign = dict_list[i]['外資']
        stock.sumING = dict_list[i]['投信']
        stock.sumDealer = dict_list[i]['自營商']
        stock.capital = dict_list[i]['股本']
        stock.industry = dict_list[i]['產業']
        stock.status = dict_list[i]['產業地位']
        stock.five = dict_list[i]['5日(%)']
        stock.ten = dict_list[i]['10日(%)']
        stock.twenty = dict_list[i]['20日(%)']
        stock.sixty = dict_list[i]['60日(%)']
        stock.one_twenty = dict_list[i]['120日(%)']
        stock.two_forty = dict_list[i]['240日(%)']
        stock.close = dict_list[i]['收盤價']
        stock.changeRate = dict_list[i]['漲跌幅(%)']
        
        j = i + 1
        while j < len(dict_list) and dict_list[i]['代碼'] == dict_list[j]['代碼']:
            stock.diff += dict_list[j]['差額(仟元)']
            stock.date.append(dict_list[j]['日期'])
            j += 1
        
        stock.date.sort(reverse=True)
        day = 0
        while day < len(stock.date) and stock.date[day] == dates[day]:
            day += 1
        stock.days = day
        
        data.append(stock)
        i = j
    
    data.sort()

    return data

def LeadertoExcel(columns, buyin_list, sellout_list, save_file_name):
    new_buyin_list = []
    new_sellout_list = []
    for item in buyin_list:
        temp = [
            item.code,
            item.name,
            item.diff,
            item.days,
            len(item.date),
            item.sumForeign,
            item.sumING,
            item.sumDealer,
            item.capital,
            item.industry,
            item.status,
            item.close,
            item.changeRate,
            item.five,
            item.ten,
            item.twenty,
            item.sixty,
            item.one_twenty,
            item.two_forty,
        ]
        new_buyin_list.append(temp)
    
    for item in sellout_list:
        temp = [
            item.code,
            item.name,
            item.diff,
            item.days,
            len(item.date),
            item.sumForeign,
            item.sumING,
            item.sumDealer,
            item.capital,
            item.industry,
            item.status,
            item.close,
            item.changeRate,
            item.five,
            item.ten,
            item.twenty,
            item.sixty,
            item.one_twenty,
            item.two_forty,
        ]
        new_sellout_list.append(temp)
    
    df_positive = pd.DataFrame(new_buyin_list, columns = columns)
    df_negative = pd.DataFrame(new_sellout_list, columns = columns)

    writer = pd.ExcelWriter(f"djangoapp/stockapp/files/Save Files/{ save_file_name }.xlsx", engine='xlsxwriter')
    df_positive.to_excel(writer, sheet_name='買入', index=False)
    df_negative.to_excel(writer, sheet_name='賣出', index=False)

    workbook = writer.book
    worksheet_positive = writer.sheets['買入']
    worksheet_negative = writer.sheets['賣出']

    worksheet_positive.set_zoom(104)
    worksheet_negative.set_zoom(104)

    formatC = workbook.add_format({'num_format': '#,##'})
    
    cols = ['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
    widths = [5.71, 7.29, 8.71, 8.71, 7.14, 7.14, 7.14, 7.71, 14.71, 54.71, 8.71, 10.14, 8.46, 8.46, 8.46, 8.46, 8.46, 8.46, 8.46, 8.43, 8.43]
    i = 0
    while i < len(cols):
        worksheet_positive.set_column(f'{cols[i]}:{cols[i]}', widths[i], None)
        worksheet_negative.set_column(f'{cols[i]}:{cols[i]}', widths[i], None)
        i += 1

    worksheet_positive.set_column('C:C', 11.57, formatC)
    worksheet_negative.set_column('C:C', 11.57, formatC)

    writer.save()


@login_required
def download(request):
    try:
        filename = f"{ request.GET['filename'] }.xlsx"
        with open(f'djangoapp/stockapp/files/Save Files/{ filename }', 'rb') as model_excel:
            result = model_excel.read()
        response = HttpResponse(result, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path(filename))

        return response
    except:
        pass

@login_required
def index(request):
    User = request.user
    title = "排行榜"
    
    file_name = []
    
    buyin_list = []
    sellout_list = []

    dates = []
    
    buy_df = pd.DataFrame()
    sellout_df = pd.DataFrame()
    
    columns = ['代碼', '股票', '差額(仟元)', '主力買超', '出現天數', '外資', '投信', '自營商', '股本', '產業', '產業地位','收盤價','漲跌幅(%)','5日(%)','10日(%)','20日(%)','60日(%)','120日(%)','240日(%)']
    
    if request.method == "POST":
        search = True
        for file in request.FILES.getlist('uploadfiles'):
            file_date = file.name.split(' ')[-1][:-5]
            dates.append(file_date)
            file_name.append(file.name.split(' ')[0])
            
            df = pd.read_excel(file, sheet_name='買入', thousands=',')
            df['日期'] = file_date
            buy_df = buy_df.append(df)

            df = pd.read_excel(file, sheet_name='賣出', thousands=',')
            df['日期'] = file_date
            sellout_df = sellout_df.append(df)
        
        dates.sort(reverse=True)

        buy_df = buy_df.reset_index()
        sellout_df = sellout_df.reset_index()
        buy_df = buy_df.drop(columns=['index', '買進', '賣出'])
        sellout_df = sellout_df.drop(columns=['index', '買進', '賣出'])
        buy_df = buy_df.sort_values(by=['代碼', '日期'], ascending = (True, False))
        sellout_df = sellout_df.sort_values(by=['代碼', '日期'], ascending = (True, False))
        
        buyin_list = CombineRepeat(list(buy_df.T.to_dict().values()), dates)
        sellout_list = CombineRepeat(list(sellout_df.T.to_dict().values()), dates)
        
        groups = groupby(file_name)
        grouped_elements = [list(group) for key, group in groups]
        file_name = ''
        for item in grouped_elements:
            file_name += item[0] + ' '

        save_file_name = f"排行榜 {file_name} { dates[0] } { dates[-1] }"
        LeadertoExcel(columns, buyin_list, sellout_list, save_file_name)
    
    return render(request, 'leaderboard.html', locals())