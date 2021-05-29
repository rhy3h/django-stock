from django.http import JsonResponse

from .wantgoo.institutional_investors import institutional_investors_data, continuous, read_csv, write_csv

def institutional_investors(request):
    stock_id = request.GET.get('stock_id')
    data = []
    
    if len(stock_id) != 4:
        return JsonResponse(data, safe=False) 
    try:
        data = read_csv('stockapp/csv/' + stock_id + '.csv')
        count = continuous(data[1:])
        data.insert(1, ['天數', count['sumForeign'], count['sumING'], count['sumDealer']])
    except:
        data = [['date', 'sumForeign', 'sumING', 'sumDealer']]
        for item in institutional_investors_data(stock_id):
            data.append(['天數', item['date'], item['sumForeign'], item['sumING'], item['sumDealer']])
        write_csv('stockapp/csv/' + stock_id + '.csv', data)
        data = read_csv('stockapp/csv/' + stock_id + '.csv')
        count = continuous(data[1:])
        data.insert(1, ['天數', count['sumForeign'], count['sumING'], count['sumDealer']])
        
    return JsonResponse(data, safe=False)