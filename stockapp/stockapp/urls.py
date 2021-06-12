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
from .group import group
from .stock import stock

handler404 = views.page_not_found
handler500 = views.internal_server_error

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', cover.index),
    path('index/', cover.index),

    path('apis/institutional_investors/<str:stock_id>/', apis.institutional_investors),

    path('header/', views.header),

    path('group/', group.base),
    path('group/create/', group.create),
    path('group/<int:group_id>/', group.index),
    path('group/<int:group_id>/sync', group.sync),
    path('group/<int:group_id>/edit', group.edit),
    path('group/<int:group_id>/delete', group.delete),
    path('group/<int:group_id>/clear', group.clear),
    path('group/<int:group_id>/upload', group.upload),
    path('group/<int:group_id>/download', group.download),
    path('group/<int:group_id>/add-broker/', group.add_broker),
    path('group/<int:group_id>/del-broker/<int:broker_id>', group.del_broker),

    path('stock/', stock.base),
    path('stock/<str:code>/', stock.index),
    path('stock/<str:code>/technical-chart/', stock.technical_chart),

    path('accounts/sign-up/', accounts.sign_up, name='sign_up'),
    path('accounts/sign-in/', accounts.sign_in, name='sign_in'),
    url('^accounts/logout', accounts.logout),
    path('accounts/profile/', accounts.profile),
]
