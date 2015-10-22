# -*-coding:utf-8-*-
from django.shortcuts import resolve_url
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from senti.sqlconnect import SqlConnect


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponse('OK')
            else:
                return HttpResponse('此帳號尚未驗證')
        else:
            return HttpResponse('帳號或密碼錯誤')
    else:
        raise PermissionDenied()


def signout(request):
    logout(request)
    return HttpResponseRedirect(resolve_url('index'))


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        exist = User.objects.filter(username=username)
        if exist:
            return HttpResponse('此帳號已被註冊')
        sc = SqlConnect(username)
        sc.create_tables()
        sc.create_sample_tags()
        User.objects.create_user(username=username, password=password)
        return HttpResponse('OK')

    else:
        raise PermissionDenied()
