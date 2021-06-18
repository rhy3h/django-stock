# [rhy3h - stock](https://rhy3h-stock.herokuapp.com/) 

[![wakatime](https://wakatime.com/badge/github/rhy3h/django-stock.svg)](https://wakatime.com/badge/github/rhy3h/django-stock) 

This is a django project for my brother 

Crawler [Fubon](https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm) and [Wantgoo](https://www.wantgoo.com/) Website's data 

UI use [AdminLTE](https://adminlte.io/) 
## First init 
```python
python stockapp/manage.py makemigrations
python stockapp/manage.py migrate
python stockapp/manage.py createsuperuser
python stockapp/manage.py makemigrations stockapp
python stockapp/manage.py migrate
``` 

## Runserver 
```python
python stockapp/manage.py runserver 127.0.0.1:8010
``` 

## Update Database 
```python
python stockapp/manage.py makemigrations stockapp
python stockapp/manage.py migrate
``` 