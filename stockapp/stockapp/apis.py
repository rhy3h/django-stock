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

def wantgoo_new(stock_id):
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
        
    return data
    
# def wantgoo_new(stock_id):
#     data = {
#         'sumForeign': 0,
#         'sumING': 0,
#         'sumDealer': 0
#     }
    
#     url = "https://www.wantgoo.com/stock/" + stock_id + "/institutional-investors/trend-data?topdays=10"

#     headers = {
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
#     }

#     resource_page = requests.get(url,headers = headers)
#     resource_page.encoding = 'utf-8'
    
#     positiveForeign = -1
#     positiveING = -1
#     positiveDealer = -1
#     negativeForeign = -1
#     negativeING = -1
#     negativeDealer = -1
    
#     try:
#         for i in range(10):
#             sumForeign = resource_page.json()[i]['sumForeignWithDealer'] + resource_page.json()[i]['sumForeignNoDealer']
#             sumING = resource_page.json()[i]['sumING']
#             sumDealer = resource_page.json()[i]['sumDealerBySelf'] + resource_page.json()[i]['sumDealerHedging']

#             if positiveForeign == -1 and sumForeign <= 0:
#                 positiveForeign = i
#             if negativeForeign == -1 and sumForeign >= 0:
#                 negativeForeign = i
            
#             if positiveING == -1 and sumING <= 0:
#                 positiveING = i
#             if negativeING == -1 and sumING >= 0:
#                 negativeING = i
            
#             if positiveDealer == -1 and sumDealer <= 0:
#                 positiveDealer = i
#             if negativeDealer == -1 and sumDealer >= 0:
#                 negativeDealer = i
        
#         if positiveForeign > negativeForeign:
#             data['sumForeign'] = positiveForeign
#         else:
#             data['sumForeign'] = -negativeForeign
#         if data['sumForeign'] == 0 and resource_page.json()[0]['sumForeignWithDealer'] + resource_page.json()[0]['sumForeignNoDealer'] != 0:
#             data['sumForeign'] = 10
        
#         if positiveING > negativeING:
#             data['sumING'] = positiveING
#         else:
#             data['sumING'] = -negativeING
#         if data['sumING'] == 0 and resource_page.json()[0]['sumING'] != 0:
#             data['sumING'] = 10
        
#         if positiveDealer > negativeDealer:
#             data['sumDealer'] = positiveDealer
#         else:
#             data['sumDealer'] = -negativeDealer
#         if data['sumDealer'] == 0 and resource_page.json()[0]['sumDealerBySelf'] + resource_page.json()[0]['sumDealerHedging'] != 0:
#             data['sumDealer'] = 10
        
#     except:
#         pass

#     return data