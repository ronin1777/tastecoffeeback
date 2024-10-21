from django.urls import path
from .views import ProductCommentsView, CommentCreateView, ReplyCommentView

app_name = 'comment'
urlpatterns = [
    path('<int:product_id>/', ProductCommentsView.as_view(), name='product-comments'),
    path('<int:product_id>/create-comment/', CommentCreateView.as_view(), name='create_comment'),
    path('reply/', ReplyCommentView.as_view(), name='reply-comment'),


]
