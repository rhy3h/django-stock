from django.shortcuts import render
from django.contrib.auth.decorators import login_required
    
from stockapp.crawler.moneydj_crawler import crawler_trading_volume, crawler_listed_trading_amount, crawler_intersection

@login_required
def trading_volume(request):
    User = request.user
    title = "市場面之成交量選股法"

    rank_list = crawler_trading_volume()

    return render(request, 'trading-volume.html', locals())

@login_required
def trading_amount(request):
    User = request.user
    title = "值大排行"

    # 0 是 上市
    # 1 是 上櫃
    if request.method == "POST":
        type = request.POST.get('type')
        days = request.POST.get('days')
    
        rank_list = crawler_listed_trading_amount(type, days)

    return render(request, 'trading-amount.html', locals())


@login_required
def intersection(request):
    User = request.user
    title = "交集"

    # 0 是 上市
    # 1 是 上櫃
    rank_list = []
    if request.method == "POST":
        type = request.POST.get('type')
        days = request.POST.get('days')
    
        rank_list = crawler_intersection(type, days)

    return render(request, 'intersection.html', locals())