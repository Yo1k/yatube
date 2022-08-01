from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from django.contrib.auth import get_user_model
from .forms import PostForm


NUM_INDEX_POST: int = 10
NUM_GROUP_POST: int = 10
NUM_USER_POST: int = 10
TITLE_LENGTH: int = 30


def index(request):
    title = 'Последние обновления на сайте'
    posts = (
        Post.objects.select_related('author')
    )
    paginator = Paginator(posts, NUM_INDEX_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, NUM_GROUP_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(
        klass=get_user_model(),
        username=username)
    user_posts = user.posts.all().select_related('group')

    paginator = Paginator(user_posts, NUM_USER_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.select_related(
        'group'
    ).select_related(
        'author'
    ).get(pk=post_id)
    num_posts = post.author.posts.count()
    context = {
        'title': post.text[:TITLE_LENGTH],
        'num_posts': num_posts,
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


@login_required()
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            Post.objects.create(
                text=form.cleaned_data['text'],
                author=request.user,
                group=form.cleaned_data['group'],
            )
            return redirect('posts:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    if not request.user.is_authenticated:
        return redirect('posts:post_detail', post_id=post_id)
    else:
        post = Post.objects.get(pk=post_id)
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post.text = form.cleaned_data['text']
                post.group = form.cleaned_data['group']
                post.save(update_fields=['text', 'group'])
                return redirect(
                    'posts:post_detail',
                    post_id=post_id
                )
        else:
            form = PostForm(instance=post)
            context = {
                'form': form,
                'is_edit': True,
                'post_id': post_id
            }
        return render(request, 'posts/create_post.html', context)
