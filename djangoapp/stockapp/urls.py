from django.urls import path, include
from django.conf.urls import url

from stockapp import broker_group

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

    path('leaderboard/', leaderboard.index),
]