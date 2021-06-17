from django.shortcuts import render, redirect
from django.contrib import auth
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import *

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '帳號'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '電子信箱'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密碼'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '確認密碼'})
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return redirect('/broker-group')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/sign-up.html', {'form': form})

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

def sign_in(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
       
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = auth.authenticate(username=username, password=password)
            
            if user is not None:
                auth.login(request, user)
                return redirect('/broker-group')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/sign-in.html', {'form': form})

def logout(request):
    auth.logout(request)
    return redirect('/accounts/sign-in')

@login_required
def profile(request):
    title = '個人檔案'
    User = request.user
    profile = Profile.objects.get_or_create(User = User)[0]
    return render(request, 'accounts/profile.html', locals())