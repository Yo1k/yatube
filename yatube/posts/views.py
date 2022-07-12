from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    title = 'Yatube: Социальная сеть блогеров'
    text = 'Это главная страница проекта Yatube'
    context = {
            'title': title,
            'text': text,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    title = 'Информация о группах'
    text = 'Здесь будет информация о группах проекта Yatube'
    context = {
            'title': title,
            'text': text,
    }
    return render(request, 'posts/group_list.html', context)
