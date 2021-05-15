from django.http import JsonResponse

import requests
from .models import Group
from .fubon import *

def wantgoo(request):
    stock_id = request.GET.get('stock_id')
    data = []
    
    url = "https://www.wantgoo.com/stock/" + stock_id + "/institutional-investors/trend-data?topdays=10"

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    resource_page = requests.get(url,headers = headers)
    resource_page.encoding = 'utf-8'
    
    for item in resource_page.json():
        temp = {}
        sumForeign = item['sumForeignWithDealer'] + item['sumForeignNoDealer']
        sumING = item['sumING']
        sumDealer = item['sumDealerBySelf'] + item['sumDealerHedging']
        
        temp['date'] = item['date'][5:10]
        temp['sumForeign'] = sumForeign
        temp['sumING'] = sumING
        temp['sumDealer'] = sumDealer
        data.append(temp)
        
    return JsonResponse(data, safe=False)