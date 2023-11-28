import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy


from blog.models import Category, Post

User = get_user_model()
MAX_POSTS_PER_PAGE = 10


def filter_by_common_attributes(posts):
    return posts.select_related('author').filter(
        is_published=True,
        pub_date__lte=datetime.datetime.now(),
        category__is_published=True
    )


def index(request):
    posts = filter_by_common_attributes(Post.objects.order_by('id'))
    paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    return render(request, 'blog/detail.html',
                  {'post': get_object_or_404(
                      filter_by_common_attributes(Post.objects),
                      pk=post_id)
                   })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    post_list = filter_by_common_attributes(category.posts).order_by('id')
    paginator = Paginator(post_list, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context,)


def profile(request, username):
    profile = get_object_or_404(User, username=username)

    posts = filter_by_common_attributes(
        Post.objects.order_by('id').filter(author=profile))
    
    paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'profile': profile, }
    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username']

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)
    

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'pub_date', 'image', 'location', 'category',]

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username
                    })

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'pub_date', 'image', 'location', 'category',]
    success_url = reverse_lazy('blog:index')
