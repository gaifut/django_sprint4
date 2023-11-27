import datetime

from django.shortcuts import get_object_or_404, render

from blog.models import Category, Post


def filter_by_common_attributes(posts):
    return posts.select_related('author').filter(
        is_published=True,
        pub_date__lte=datetime.datetime.now(),
        category__is_published=True
    )


def index(request):
    return render(
        request, 'blog/index.html',
        {'post_list': filter_by_common_attributes(Post.objects)[0:5]}
    )


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

    return render(
        request, 'blog/category.html',
        {'post_list': filter_by_common_attributes(category.posts),
         'category': category,
         })
