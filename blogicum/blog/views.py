import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView, DeleteView, TemplateView, UpdateView
)
from django.urls import reverse

from blog.models import Category, Comments, Post, User
from blogicum.settings import MAX_POSTS_PER_PAGE
from .forms import CommentsForm


def filter_by_common_attributes(posts):
    return posts.select_related('author').filter(
        is_published=True,
        pub_date__lte=datetime.datetime.now(),
        category__is_published=True
    )


def page_obj(request, posts):
    return Paginator(
        posts,
        MAX_POSTS_PER_PAGE
    ).get_page(
        request.GET.get('page')
    )


def annotate_comment_count(posts):
    return posts.annotate(
        comment_count=Count(
            'comments')).order_by('-pub_date')


class IndexView(TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = filter_by_common_attributes(
            annotate_comment_count(Post.objects)
        )
        context['page_obj'] = page_obj(
            self.request,
            posts
        )
        return context


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        post = get_object_or_404(
            filter_by_common_attributes(
                Post.objects), pk=post_id)

    return render(
        request, 'blog/detail.html', {
            'post': post,
            'form': CommentsForm(),
            'comments': post.comments.select_related('author')
        })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    return render(
        request, 'blog/category.html', {
            'page_obj': page_obj(
                request, annotate_comment_count(
                    filter_by_common_attributes(category.posts))),
            'category': category
        })


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts_query = profile.posts.all()

    if request.user != profile:
        posts_query = filter_by_common_attributes(posts_query)

    return render(
        request,
        'blog/profile.html', {
            'page_obj': page_obj(
                request, annotate_comment_count(posts_query)),
            'profile': profile
        })


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username']

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username
                                    })


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'pub_date', 'image', 'location', 'category', ]

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username
                    })

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'pub_date', 'image', 'location', 'category', ]

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username
                    })

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id)

    def form_valid(self, form):
        if self.request.user == self.get_object().author:
            form.instance.author = self.request.user
            return super().form_valid(form)
        return redirect(reverse('blog:post_detail', args=(form.instance.id,)))


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentsForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comments, pk=comment_id, post=post_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentsForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        'blog/comment.html',
        {'form': form, 'comment': comment
         })


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username
                    })

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id, author=self.request.user)

    def form_valid(self, form):
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comments, pk=comment_id, post=post_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=comment.post.id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
