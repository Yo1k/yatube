from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('Wellcome to the Yatube.')


def group_posts(request, slug):
    return HttpResponse('Here post for group: %s' % slug)
