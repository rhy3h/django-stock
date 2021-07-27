from django.urls import path, include
from django.conf.urls import url

from stockapp import broker_group, leaderboard, stock_group, stock

from stockapp.crawler import wantgoo
from stockapp import leaderboard

urlpatterns = [
    path('crawler/institutional_investors/<str:code>/<str:end_date>/', wantgoo.read_institutional_investors),
    path('crawler/count/institutional_investors/<str:code>/<str:end_date>/', wantgoo.count_read_institutional_investors),

    path('broker-group/', broker_group.base),
    path('broker-group/create/', broker_group.create),
    path('broker-group/<int:group_id>/', broker_group.index),
    path('broker-group/<int:group_id>/edit', broker_group.edit),
    path('broker-group/<int:group_id>/delete', broker_group.delete),
    path('broker-group/<int:group_id>/upload', broker_group.upload),
    path('broker-group/<int:group_id>/sync/', broker_group.sync),
    path('broker-group/<int:group_id>/download/', broker_group.download),

    path('leaderboard/', leaderboard.index),
    path('leaderboard/download', leaderboard.download),

    path('stock-group/', stock_group.base),
    path('stock-group/create/', stock_group.create),
    path('stock-group/<int:group_id>/', stock_group.index),
    path('stock-group/<int:group_id>/add', stock_group.add),
    path('stock-group/<int:group_id>/edit', stock_group.edit),
    path('stock-group/<int:group_id>/delete', stock_group.delete),
    path('stock-group/<int:group_id>/delete/<int:stock_item_id>', stock_group.delete_item),

    path('stock/', stock.base),
    path('stock/<int:code>/', stock.index),
    path('stock/<int:code>/add', stock.add),
    path('stock/<int:code>/delete', stock.delete),
    path('stock/<int:code>/backtesting', stock.backtesting),
]