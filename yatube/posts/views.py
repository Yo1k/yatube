from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

NUM_INDEX_POST: int = 10
NUM_GROUP_POST: int = 10
NUM_USER_POST: int = 10


def get_page_obj(request, object_list, per_page):
    paginator = Paginator(object_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    title = 'Последние обновления на сайте'
    posts = (
        Post.objects.select_related('author')
    )
    page_obj = get_page_obj(request, posts, NUM_INDEX_POST)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_obj(request, posts, NUM_GROUP_POST)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(
        klass=get_user_model(),
        username=username
    )
    posts = user.posts.select_related('group')
    page_obj = get_page_obj(request, posts, NUM_USER_POST)
    context = {
        'page_obj': page_obj,
        'profile': user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        klass=Post.objects.select_related('group', 'author'),
        id=post_id)
    num_posts = post.author.posts.count()
    context = {
        'num_posts': num_posts,
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    form = PostForm(request.POST or None)

    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post_id and request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, 'posts/create_post.html', context)
