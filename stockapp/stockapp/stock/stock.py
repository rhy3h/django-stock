from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ..models import Group

import requests
import csv

@login_required
def base(request):
    User = request.user
    group_list = Group.objects.filter(Owner=User)
    title = '股票'

    with open('stockapp/static/js/stock.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stocks = list(reader)

    return render(request, 'stock/index.html', locals())

@login_required
def index(request, code):
    User = request.user
    group_list = Group.objects.filter(Owner=User)
    title = '股票'

    with open('stockapp/static/js/stock.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stocks = list(reader)

    return render(request, 'stock/index.html', locals())

def financial_statements(request, code):
    User = request.user
    group_list = Group.objects.filter(Owner=User)
    title = '股票'
    
    with open('stockapp/static/js/stock.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stocks = list(reader)

    return render(request, 'stock/financial-statements.html', locals())

def financial_statements_api(request, code):
    data = [
        {
            "stockNo": code,
            "date": "2021-04-01T00:00:00",
            "monthRevenue": 0,
            "preMonthRevenue": 0,
            "preYearMonthRevenue": 0,
            "preMonthRevenueDiff": 50,
            "preYearMonthRevenueDiff": -50,
            "monthTotalRevenue": 0,
            "preYearTotalRevenue": 0,
            "preTotalRevenueDiff": 0,
            "close": 0
        }
    ]

    url = "https://www.wantgoo.com/stock/" + code + "/financial-statements/monthly-revenue-data"
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    try:
        data = resource_page.json()
    except:
        pass
    
    return JsonResponse(data, safe=False)