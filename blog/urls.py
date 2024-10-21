from django.urls import path
from .views import BlogPostList, BlogPostDetail

app_name = 'blog'

urlpatterns = [
    path('blog/', BlogPostList.as_view(), name='blog_post_list'),
    path('blog/<int:pk>/', BlogPostDetail.as_view(), name='blog_post_detail'),
]