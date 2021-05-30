import requests
from django.http import  JsonResponse

def api(url):
    data = []

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    }

    resource_page = requests.get(url, headers = headers)
    resource_page.encoding = 'utf-8'
    
    try:
        data = resource_page.json()
    except:
        pass
    
    return data