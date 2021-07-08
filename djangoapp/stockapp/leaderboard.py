from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import pandas as pd

from itertools import groupby

class Stock:
    def __init__(self, code, name, diff):
        self.code = code
        self.name = name
        self.diff = diff
        self.date = []
        self.days = None
        self.sumForeign = None
        self.sumING = None
        self.sumDealer = None
        self.capital = None
        self.industry = None
        self.status = None
    
    def __lt__(self, other):
        return self.code < other.code

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

    return data

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

    if request.method == "POST":
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
        
        # buyin_list.sort()
        # sellout_list.sort()
        buy_df.sort_values(by=['差額(仟元) ', 'col2'])
        print(buy_df)

        buyin_list = CombineRepeat(list(buy_df.T.to_dict().values()), dates)
        sellout_list = CombineRepeat(list(sellout_df.T.to_dict().values()), dates)

        groups = groupby(file_name)
        grouped_elements = [list(group) for key, group in groups]
        file_name = ''
        for item in grouped_elements:
            file_name += item[0] + ' '
    
    return render(request, 'leaderboard.html', locals())