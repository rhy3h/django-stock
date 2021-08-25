# [rhy3h - stock](https://rhy3h-stock.herokuapp.com/) 

[![wakatime](https://wakatime.com/badge/github/rhy3h/django-stock.svg)](https://wakatime.com/badge/github/rhy3h/django-stock) 

This is a django crawler project for my brother 

Crawler [Broker](https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm), [Historical Daily Candlesticks](https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcw/zcw1_2330.djhtm), 
[Institutional Investors](https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl_2330.djhtm) Website's data 

UI use [AdminLTE](https://adminlte.io/) 

## Activate your python environment

## First init 
```python
python djangoapp/manage.py makemigrations
python djangoapp/manage.py migrate
python djangoapp/manage.py createsuperuser
python djangoapp/manage.py makemigrations stockapp
python djangoapp/manage.py migrate
``` 

## Runserver 
```python
python djangoapp/manage.py runserver 127.0.0.1:8010
``` 

## Update Database 
```python
python djangoapp/manage.py makemigrations stockapp
python djangoapp/manage.py migrate
``` 