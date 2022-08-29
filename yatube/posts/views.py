from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


# utils
def get_page_obj(request, object_list, per_page):
    paginator = Paginator(object_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


# views
@login_required()
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required()
def follow_index(request):
    posts = Post.objects.select_related(
        'author', 'group'
    ).filter(author__following__user=request.user)
    page_obj = get_page_obj(request, posts, settings.NUM_INDEX_POST)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page_obj = get_page_obj(request, posts, settings.NUM_GROUP_POST)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@cache_page(20, key_prefix='index_page')
@vary_on_cookie
def index(request):
    title = 'Последние обновления на сайте'
    posts = Post.objects.select_related('author', 'group')
    page_obj = get_page_obj(request, posts, settings.NUM_INDEX_POST)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


@login_required()
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'comments': post.comments.all(),
        'form': CommentForm(),
        'num_posts': post.author.posts.count(),
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post_id and request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, 'posts/post_create.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    page_obj = get_page_obj(request, posts, settings.NUM_USER_POST)

    # The condition in the `filter` covers both situations: when user is
    # authorized and anonymous, in comparison with the condition
    # `user=request.user`, that falls with the error in the case of an
    # anonymous client.
    following = author.following.filter(user__id=request.user.id).exists()

    context = {
        'following': following,
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


@login_required()
@require_http_methods(['POST'])
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(author=author, user=request.user)

    return redirect('posts:profile', username=username)


@login_required()
@require_http_methods(['POST'])
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username=username)
