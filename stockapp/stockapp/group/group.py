from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.utils.encoding import escape_uri_path

from datetime import date, datetime, timedelta

from ..models import Group, Broker
from ..fubon.fubon import fubon_get_list, get_id_name, get_branch
from ..wantgoo.institutional_investors import institutional_investors_data, stock_append_data

import os, csv, codecs

def progress_bar(count, length):
    print("[%-25s] %d/%d (%d%%)" % ('='*(int)(count / length * 25), count, length, (count / length * 100)), end='\r')

@login_required
def base(request):
    User = request.user
    group_list = Group.objects.filter(Owner=User)
    title = '群組'
    
    with open('stockapp/static/js/stock.csv', newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        stocks = list(reader)
    
    return render(request, 'group/index.html', locals())
    
def read_csv(file):
    data = []
    with open(file, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

def write_csv(path, stock):
    data = [['date', 'sumForeign', 'sumING', 'sumDealer']]
    for item in institutional_investors_data(stock):
        data.append([item['date'], item['sumForeign'], item['sumING'], item['sumDealer']])
    
    with open(path + stock + '.csv', "a", newline = "") as f:
        writer = csv.writer(f)
        
        for row in data:
            writer.writerow(row)
    return True

@login_required
def sync(request, group_id):
    stock_list = read_csv('stockapp/stock_list.csv')
    path = 'stockapp/csv/'
    length = len(stock_list)
    count = 1

    begin_time = datetime.now()
    print("開始時間: ", begin_time.strftime('%H:%M:%S'))

    for stock in stock_list:
        try:
            os.remove(path + stock[0] + '.csv')
        except:
            pass
        write_csv(path, stock[0])
        progress_bar(count, length)
        count += 1
    print()

    end_time = datetime.now()
    print("結束時間: ", end_time.strftime('%H:%M:%S'))
    
    print("爬蟲時間", end_time - begin_time)

    return JsonResponse([], safe=False)

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

    if request.POST.get('search'):
        if request.POST.get('end_date') != '':
            begin_date = request.POST.get('begin_date')
            begin_datatime = datetime.strptime(begin_date, "%Y-%m-%d")
            end_date = request.POST.get('end_date')
            end_datatime = datetime.strptime(end_date, "%Y-%m-%d")

            if end_datatime.isoweekday() > 5:
                end_date = (end_datatime + timedelta(days = (5 - end_datatime.isoweekday()))).strftime("%Y-%m-%d")
            if begin_datatime.isoweekday() > 5:
                begin_date = (begin_datatime + timedelta(days = (5 - begin_datatime.isoweekday()))).strftime("%Y-%m-%d")

            if begin_date > end_date:
                begin_date, end_date = end_date, begin_date
            if begin_date == '':
                begin_date = end_date

        broker_branch = []
        for broker in broker_list:
            broker_branch.append([broker.Broker, broker.Branch])
        stock_list = fubon_get_list(broker_branch, begin_date, end_date)
        for item in stock_list['positive']:
            item = stock_append_data(item, end_date)
        for item in stock_list['negative']:
            item = stock_append_data(item, end_date)
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
def clear(request, group_id):
    User = request.user
    group_list = Group.objects.filter(Owner=User)
    group = group_list.get(id = group_id)
    broker_list = Broker.objects.filter(Group = group)
    for broker in broker_list:
        broker.delete()

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
        writer.writerow([broker.Name])

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