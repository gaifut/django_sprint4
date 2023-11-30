import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseRedirect


from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView, DeleteView, TemplateView, UpdateView
)
from django.urls import reverse_lazy

from blog.models import Category, Post, Comments
from .forms import CommentsForm

User = get_user_model()
MAX_POSTS_PER_PAGE = 10


def filter_by_common_attributes(posts):
    return posts.select_related('author').filter(
        is_published=True,
        pub_date__lte=datetime.datetime.now(),
        category__is_published=True
    )


class Index(TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = filter_by_common_attributes(Post.objects.order_by('-pub_date'))
        paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


def post_detail(request, post_id):
    form = CommentsForm()
    # comments = get_object_or_404(
    #                   filter_by_common_attributes(Post.objects),
    #                   pk=post_id).comments.select_related('author')

    # return render(request, 'blog/detail.html',
    #               {'post': get_object_or_404(
    #                   filter_by_common_attributes(Post.objects),
    #                   pk=post_id),
    #                   'form': form,
    #                   'comments': comments
    #                })

    post = get_object_or_404(Post, pk=post_id)

    if post.is_published or (
        request.user.is_authenticated and request.user == post.author
    ):
        comments = post.comments.select_related('author')
        return render(
            request, 'blog/detail.html', {
                'post': post,
                'form': form,
                'comments': comments
            })
    else:
        return render(request, '404.html', status=404)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    post_list = filter_by_common_attributes(
        category.posts).order_by('-pub_date')
    paginator = Paginator(post_list, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context,)


def profile(request, username):
    profile = get_object_or_404(User, username=username)

    # posts = Post.objects.filter(author=profile)

    # paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    # context = {'page_obj': page_obj, 'profile': profile, }
    # return render(request, 'blog/profile.html', context)

    if request.user == profile:
        posts = Post.objects.filter(author=profile)
    else:
        posts = Post.objects.filter(author=profile,
                                    is_published=True,
                                    pub_date__lte=datetime.datetime.now()
                                    )

    paginator = Paginator(posts, MAX_POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'profile': profile}

    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username']

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username
                                    })


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = ['title', 'text', 'pub_date', 'image', 'location', 'category', ]

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
    fields = ['title', 'text', 'pub_date', 'image', 'location', 'category', ]

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username
                    })

    def get(self, request, *args, **kwargs):
        if (self.request.user.is_authenticated
                and self.request.user == self.get_object().author):
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(
                reverse_lazy('blog:post_detail', kwargs={
                    'post_id': self.kwargs['pk']
                }))

    def form_valid(self, form):
        if (self.request.user.is_authenticated
                and self.request.user == self.get_object().author):
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            return HttpResponseRedirect(
                reverse_lazy('blog:post_detail', kwargs={
                    'post_id': form.instance.id
                }))


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
        return HttpResponseForbidden(
            'У вас нет прав на изменение этого комментария.'
        )

    form = CommentsForm(request.POST or None, instance=comment)
    context = {'form': form, 'comment': comment}
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username
                    })

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        if (self.request.user.is_authenticated
                and self.request.user == post.author):
            return super().delete(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(
                "You don't have permission to delete this post."
            )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comments, pk=comment_id, post=post_id)

    if request.user != comment.author:
        return HttpResponseForbidden(
            'У вас нет прав на удаление этого комментария.'
        )
    context = {'comment': comment}
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
