from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.utils.encoding import escape_uri_path

from datetime import date, datetime, timedelta

from stockapp.models import *

from stockapp.crawler.fubon import NameToID, CrawlerList

import os, csv, codecs

from stockapp.crawler import wantgoo

import pandas as pd

@login_required
def base(request):
    User = request.user
    broker_group_list = BrokerGroup.objects.filter(
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
        BrokerGroup.objects.get_or_create(
            Owner = User,
            Name = new_group_name
        )
        broker_group = BrokerGroup.objects.filter(
            Owner=User
        ).last()

        return redirect('/broker-group/' + str(broker_group.id))

@login_required
def edit(request, group_id):
    if request.method == "POST":
        User = request.user
        edit_group_name = request.POST['edit-group-name']
        broker_group = BrokerGroup.objects.get(
            Owner = User,
            id = group_id
        )
        broker_group.Name = edit_group_name
        broker_group.save()
    
    return redirect('/broker-group/' + str(group_id))

@login_required
def upload(request, group_id):
    User = request.user
    broker_group = BrokerGroup.objects.filter(
        Owner = User
    ).get(
        id = group_id
    )
    broker_list = Broker.objects.filter(
        BrokerGroup = broker_group
    )
    
    if request.method == "POST":
        for broker in broker_list:
            broker.delete()

        uploadfile = request.FILES['uploadfile']
        data = pd.read_excel(uploadfile)['名稱'].values.tolist()
        
        for item in data:
            if item[0] == '奔':
                item = '(牛牛牛)' + item[1:]
            broker_branch = NameToID(item)
            Broker.objects.get_or_create(
                BrokerGroup = broker_group,
                Name = item,
                Broker = broker_branch['broker_id'],
                Branch = broker_branch['branch_id']
            )
    
    return redirect('/broker-group/' + str(group_id))

@login_required
def sync(request, group_id):
    
    wantgoo.sync_institutional_investors()
    
    return JsonResponse([], safe=False)

@login_required
def delete(request, group_id):
    if request.method == "POST":
        User = request.user
        broker_group = BrokerGroup.objects.get(
            Owner = User,
            id = group_id
        )
        broker_group.delete()

    return redirect('/broker-group/')

class ClsBroker:
    def __init__(self, broker, branch):
        self.broker_code = broker
        self.branch_code = branch

@login_required
def index(request, group_id):
    User = request.user
    broker_group_list = BrokerGroup.objects.filter(
        Owner = User
    )
    broker_group = broker_group_list.get(
        id = group_id
    )
    title = '群組 ' + broker_group.Name
    broker_list = Broker.objects.filter(
        BrokerGroup = broker_group
    )
    today = date.today().strftime("%Y-%m-%d")
    begin_date = today
    end_date = today

    if request.POST.get('search'):
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

    return render(request, 'broker-group.html', locals())