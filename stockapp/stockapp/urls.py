"""stockapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.contrib.auth.views import LoginView
from . import views, apis, accounts
from .cover import cover
from .broker_group import broker_group
from .stock_group import stock_group
from .leaderboard import leaderboard

handler404 = views.page_not_found
handler500 = views.internal_server_error

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', cover.index),
    path('index/', cover.index),

    path('apis/institutional_investors/<str:stock_id>/<str:end_date>/', apis.institutional_investors),

    path('header/', views.header),

    path('broker-group/', broker_group.base),
    path('broker-group/create/', broker_group.create),
    path('broker-group/<int:group_id>/', broker_group.index),
    path('broker-group/<int:group_id>/edit', broker_group.edit),
    path('broker-group/<int:group_id>/delete', broker_group.delete),
    path('broker-group/<int:group_id>/upload', broker_group.upload),
    path('broker-group/<int:group_id>/sync/', broker_group.sync),
    
    path('stock-group/', stock_group.base),
    path('stock-group/create/', stock_group.create),
    path('stock-group/<int:group_id>/', stock_group.index),
    path('stock-group/<int:group_id>/add', stock_group.add),
    path('stock-group/<int:group_id>/edit', stock_group.edit),
    path('stock-group/<int:group_id>/delete', stock_group.delete),

    path('leaderboard/', leaderboard.index),

    path('accounts/sign-up/', accounts.sign_up, name='sign_up'),
    path('accounts/sign-in/', accounts.sign_in, name='sign_in'),
    url('^accounts/logout', accounts.logout),
    path('accounts/profile/', accounts.profile),
]