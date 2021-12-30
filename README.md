# [rhy3h - stock](https://rhy3h-stock.herokuapp.com/)

[![Python 3.7.11](https://img.shields.io/badge/python-3.7.11-blue.svg)](https://www.python.org/downloads/release/python-3711/)
[![wakatime](https://wakatime.com/badge/github/rhy3h/django-stock.svg)](https://wakatime.com/badge/github/rhy3h/django-stock)

這是一個為了我哥寫的股票爬蟲網站

爬取 [券商](https://fubon-ebrokerdj.fbs.com.tw/z/zg/zgb/zgb0.djhtm), [歷史股價](https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcw/zcw1_2330.djhtm),
[法人動態](https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl_2330.djhtm) 的網站資料

UI 使用 [AdminLTE](https://adminlte.io/)

## Candlestick chart

<img src="./img/candlestick-chart-demo.gif" alt="candlestick-chart-demo" align=center />

## Activate your python environment

```shell
pip install -r requirements.txt
```

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

## Update database

```python
python djangoapp/manage.py makemigrations stockapp
python djangoapp/manage.py migrate
```
