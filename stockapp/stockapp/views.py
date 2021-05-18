from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth

def page_not_found(request, exception=None):
    title = '404'
    return render(request, 'error/404.html', locals())

def internal_server_error(request, exception=None):
    title = '500'
    return render(request, 'error/500.html', locals())

def register(request):
    return render(request, 'error/404.html', locals())

def logout(request):
    auth.logout(request)
    return redirect('/accounts/sign-in')