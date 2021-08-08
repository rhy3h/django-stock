from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from stockapp import models
from stockapp.crawler.fubon import NameToID, CrawlerList, ListtoExcel
from stockapp.crawler import wantgoo

from django.utils.encoding import escape_uri_path

from datetime import date, datetime, timedelta
import pandas as pd


@login_required
def base(request):
    User = request.user
    broker_group_list = models.BrokerGroup.objects.filter(
        Owner = User
    )
    
    try:
        return redirect('/broker-group/' + str(broker_group_list.first().id))
    except:
        return render(request, 'broker-group.html', locals())
    
@login_required
def create(request):
    if request.method == "POST":
        new_group_name = request.POST['new-group-name']
        User = request.user
        models.BrokerGroup.objects.get_or_create(
            Owner = User,
            Name = new_group_name
        )
        broker_group = models.BrokerGroup.objects.filter(
            Owner=User
        ).last()

        return redirect('/broker-group/' + str(broker_group.id))

@login_required
def edit(request, group_id):
    if request.method == "POST":
        User = request.user
        edit_group_name = request.POST['edit-group-name']
        broker_group = models.BrokerGroup.objects.get(
            Owner = User,
            id = group_id
        )
        broker_group.Name = edit_group_name
        broker_group.save()
    
    return redirect('/broker-group/' + str(group_id))

@login_required
def upload(request, group_id):
    User = request.user
    broker_group = models.BrokerGroup.objects.filter(
        Owner = User
    ).get(
        id = group_id
    )
    broker_list = models.BrokerGroupItem.objects.filter(
        BrokerGroup = broker_group
    )
    
    if request.method == "POST":
        for broker in broker_list:
            broker.delete()

        uploadfile = request.FILES['uploadfile']
        data = pd.read_excel(uploadfile)['名稱'].values.tolist()
        
        for item in data:
            broker_branch = NameToID(item)
            models.BrokerGroupItem.objects.get_or_create(
                BrokerGroup = broker_group,
                Name = item,
                Broker = broker_branch['broker_id'],
                Branch = broker_branch['branch_id']
            )
    
    return redirect('/broker-group/' + str(group_id))

@login_required
def sync(request, group_id):
    
    wantgoo.sync()
    
    return JsonResponse([], safe=False)

@login_required
def delete(request, group_id):
    if request.method == "POST":
        User = request.user
        broker_group = models.BrokerGroup.objects.get(
            Owner = User,
            id = group_id
        )
        broker_group.delete()

    return redirect('/broker-group/')

@login_required
def download(request, group_id):
    try:
        filename = f"{ request.GET['filename'] }.xlsx"
        with open(f'djangoapp/stockapp/files/Save Files/{ filename }', 'rb') as model_excel:
            result = model_excel.read()
        response = HttpResponse(result, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path(filename))

        return response
    except:
        pass

class ClsBroker:
    def __init__(self, broker, branch):
        self.broker_code = broker
        self.branch_code = branch

import time

@login_required
def index(request, group_id):
    User = request.user
    broker_group_list = models.BrokerGroup.objects.filter(
        Owner = User
    )
    broker_group = broker_group_list.get(
        id = group_id
    )
    title = '群組 ' + broker_group.Name
    broker_list = models.BrokerGroupItem.objects.filter(
        BrokerGroup = broker_group
    )
    today = date.today().strftime("%Y-%m-%d")
    begin_date = today
    end_date = today
    
    columns = [
        '代碼',
        '股票',
        '差額(仟元)',
        '外資',
        '投信',
        '自營商',
        '股本',
        '產業',
        '產業地位',
        '收盤價',
        '漲跌幅(%)',
        '5日(%)',
        '10日(%)',
        '20日(%)',
        '60日(%)',
        '120日(%)',
        '240日(%)',
        '買進',
        '賣出',
    ]
    
    if request.method == "POST":
        search = True
        begin_date = request.POST.get('begin-date')
        begin_datatime = datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = request.POST.get('end-date')
        end_datatime = datetime.strptime(end_date, "%Y-%m-%d")

        if end_datatime.isoweekday() > 5:
            end_date = (end_datatime + timedelta(days = (5 - end_datatime.isoweekday()))).strftime("%Y-%m-%d")
        if begin_datatime.isoweekday() > 5:
            begin_date = (begin_datatime + timedelta(days = (5 - begin_datatime.isoweekday()))).strftime("%Y-%m-%d")

        if begin_date > end_date:
            begin_date, end_date = end_date, begin_date

        broker_branch = []
        for broker in broker_list:
            broker_branch.append(ClsBroker(broker.Broker, broker.Branch))
        stock_table = CrawlerList(broker_branch, begin_date, end_date)
        save_file_name = f"{broker_group.Name} {begin_date} {end_date}"
        ListtoExcel(stock_table, save_file_name)
        
    return render(request, 'broker-group.html', locals())