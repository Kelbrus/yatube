from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post


DISPLAYED_COUNT = 10

User = get_user_model()


def makes_paginator(request, obj_list):

    paginator = Paginator(obj_list, DISPLAYED_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):

    post_list = Post.objects.select_related('group')

    page_obj = makes_paginator(request, post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.select_related('group')
    page_obj = makes_paginator(request, posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):

    author = get_object_or_404(User, username=username)

    post_list = Post.objects.filter(author=author)
    page_obj = makes_paginator(request, post_list)
    template = 'posts/profile.html'
    context = {'page_obj': page_obj, 'author': author}
    return render(request, template, context)


def post_detail(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    posts_count = Post.objects.filter(author=post.author).count()
    template = 'posts/post_detail.html'
    context = {'post': post, 'posts_count': posts_count}
    return render(request, template, context)


@login_required
def post_create(request):

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        # instance=post,
    )

    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    template = 'posts/create_post.html'
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):

    edit_post = get_object_or_404(Post, id=post_id)

    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=edit_post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {'form': form, 'is_edit': True}
    return render(request, template, context)
