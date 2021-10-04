from django.http.response import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse('ГЛАВНАЯ страница')

def group_posts(request, slug):
    return HttpResponse('Постики))')
