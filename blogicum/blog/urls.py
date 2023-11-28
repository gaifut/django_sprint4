from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit',views.PostUpdateView.as_view(), name='edit_post'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<str:username>/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('', views.index, name='index'),
]
