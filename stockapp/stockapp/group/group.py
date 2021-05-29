from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User

from django.utils.encoding import escape_uri_path

from ..models import Group, Broker
from django.http import JsonResponse
from ..fubon.fubon import *

import csv, codecs

from datetime import date

import os

@login_required
def base(request):
    User = request.user
    group_list = Group.objects.filter(Owner=User)
    title = '群組'
    
    with open('stockapp/static/js/stock.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stocks = list(reader)
    
    return render(request, 'group/index.html', locals())

def write_csv(file, data):
    with open(file, "a", newline = "") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)
    return data

def read_csv(file):
    data = []
    with open(file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

def continuous(stock_data):
    positiveForeign = -1
    positiveING = -1
    positiveDealer = -1
    negativeForeign = -1
    negativeING = -1
    negativeDealer = -1

    for i in range(1, len(stock_data)):
        sumForeign = int(stock_data[i][1])
        sumING = int(stock_data[i][2])
        sumDealer = int(stock_data[i][3])

        if positiveForeign == -1 and sumForeign <= 0:
            positiveForeign = i
        if negativeForeign == -1 and sumForeign >= 0:
            negativeForeign = i
        
        if positiveING == -1 and sumING <= 0:
            positiveING = i
        if negativeING == -1 and sumING >= 0:
            negativeING = i
        
        if positiveDealer == -1 and sumDealer <= 0:
            positiveDealer = i
        if negativeDealer == -1 and sumDealer >= 0:
            negativeDealer = i
    
    data = {
        'sumForeign': 0,
        'sumING': 0,
        'sumDealer': 0
    }
    if positiveForeign > negativeForeign:
        data['sumForeign'] = positiveForeign
    else:
        data['sumForeign'] = -negativeForeign
    if data['sumForeign'] == 0 and int(stock_data[0][1]) != 0:
        data['sumForeign'] = 10
    
    if positiveING > negativeING:
        data['sumING'] = positiveING
    else:
        data['sumING'] = -negativeING
    if data['sumING'] == 0 and int(stock_data[0][2]) != 0:
        data['sumING'] = 10
    
    if positiveDealer > negativeDealer:
        data['sumDealer'] = positiveDealer
    else:
        data['sumDealer'] = -negativeDealer
    if data['sumDealer'] == 0 and int(stock_data[0][3]) != 0:
        data['sumDealer'] = 10
    
    return data

def stock_append_data(item, date):
    stock_id = item['id']
    if len(stock_id) == 5:
        return item
    try:
        stock_data = read_csv('stockapp/csv/' + stock_id + '.csv')
        if date == stock_data[1][0]:
            count = continuous(stock_data[1:])
            item['sumForeign'] = count['sumForeign']
            item['sumING'] = count['sumING']
            item['sumDealer'] = count['sumDealer']
        else:
            os.remove('stockapp/csv/' + stock_id + '.csv')
            data = [['date', 'sumForeign', 'sumING', 'sumDealer']]
            for item in wantgoo_new(stock_id):
                data.append([item['date'], item['sumForeign'], item['sumING'], item['sumDealer']])
            write_csv('stockapp/csv/' + stock_id + '.csv', data)
            print("write file")
    except:
        data = [['date', 'sumForeign', 'sumING', 'sumDealer']]
        for item in wantgoo_new(stock_id):
            data.append([item['date'], item['sumForeign'], item['sumING'], item['sumDealer']])
        write_csv('stockapp/csv/' + stock_id + '.csv', data)
        print("write file")
        stock_data = read_csv('stockapp/csv/' + stock_id + '.csv')
        count = continuous(stock_data[1:])
        item['sumForeign'] = count['sumForeign']
        item['sumING'] = count['sumING']
        item['sumDealer'] = count['sumDealer']
    
    return item

@login_required
def index(request, group_id):
    User = request.user
    group_list = Group.objects.filter(Owner=User)
    group = group_list.get(id = group_id)
    
    title = '群組 ' + group.Name
    broker_list = Broker.objects.filter(Group = group)
    today = date.today().strftime("%Y-%m-%d")
    begin_date = today
    end_date = today

    if request.method == 'POST':
        if request.POST.get('end_date') != '':
            begin_date = request.POST.get('begin_date')
            end_date = request.POST.get('end_date')
            if begin_date > end_date:
                begin_date, end_date = end_date, begin_date
            if begin_date == '':
                begin_date = end_date
        broker_branch = []
        for broker in broker_list:
            broker_branch.append([broker.Broker, broker.Branch])
        stock_list = fubon_get_list(broker_branch, begin_date, end_date)
        length = len(stock_list['positive']) + len(stock_list['negative'])
        count = 0
        stock = wantgoo_new('2330')
        for item in stock_list['positive']:
            item = stock_append_data(item, stock[0]['date'])
            
            print('%d / %d' % (count, length))
            count += 1
        for item in stock_list['negative']:
            item = stock_append_data(item, stock[0]['date'])
            
            print('%d / %d' % (count, length))
            count += 1
        
    with open('stockapp/static/js/stock.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stocks = list(reader)

    return render(request, 'group/index.html', locals())

@login_required
def create(request):
    if request.method == "POST":
        group_name = request.POST['group_name']
        User = request.user
        Group.objects.get_or_create(Owner = User,
                                Name = group_name)
        group = Group.objects.filter(Owner=User).last()

        return redirect('/group/' + str(group.id))

@login_required
def edit(request, group_id):
    if request.method == "POST":
        new_group_name = request.POST['new_group_name']
        User = request.user
        group = Group.objects.get(Owner = User,
                            id = group_id)
        group.Name = new_group_name
        group.save()
    
    return redirect('/group/' + str(group_id))

@login_required
def delete(request, group_id):
    User = request.user
    group = Group.objects.get(Owner = User,
                        id = group_id)
    group.delete()

    return redirect('/group/')

@login_required
def add_broker(request, group_id):
    if request.method == "POST":
        User = request.user
        group = Group.objects.filter(Owner=User).get(id = group_id)
        broker = str(request.POST['select_broker'])
        branch = str(request.POST['select_branch'])
        
        Broker.objects.get_or_create(Group = group,
                                Name = get_id_name(branch).name,
                                Broker = broker,
                                Branch = branch)
        
        return redirect('/group/' + str(group_id))

@login_required
def del_broker(request, group_id, broker_id):
    User = request.user
    group = Group.objects.filter(Owner = User).get(id = group_id)
    broker = Broker.objects.filter(Group = group).get(id = broker_id)
    broker.delete()
    
    return redirect('/group/' + str(group_id))

@login_required
def download(request, group_id):
    User = request.user
    group = Group.objects.filter(Owner = User).get(id = group_id)
    broker_list = Broker.objects.filter(Group = group)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment;filename={}".format(escape_uri_path(group.Name + ".csv"))
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)

    for broker in broker_list:
        writer.writerow([broker.Name,broker.Broker, broker.Branch])

    return response

@login_required
def upload(request, group_id):
    User = request.user
    group = Group.objects.filter(Owner = User).get(id = group_id)
    
    if request.method == "POST":
        uploadfile = request.FILES['uploadfile']
        for line in uploadfile:
            string = line.decode("utf-8-sig")
            name = string.split(',')[0].replace("\r\n","")
            broker_branch = get_branch(name)
            Broker.objects.get_or_create(Group = group,
                                Name = name,
                                Broker = broker_branch[0],
                                Branch = broker_branch[1])
    return redirect('/group/' + str(group_id))