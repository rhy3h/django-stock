from django.http import JsonResponse

from .wantgoo.institutional_investors import continuous, read_csv

def institutional_investors(request, stock_id):
    data = []
    
    if len(stock_id) != 4:
        return JsonResponse(data, safe=False) 
    try:
        data = read_csv('stockapp/csv/' + stock_id + '.csv')
        count = continuous(data[1:])
        # data.insert(1, ['天數', count['sumForeign'], count['sumING'], count['sumDealer']])
    except:
        pass
        
    return JsonResponse(data, safe=False)