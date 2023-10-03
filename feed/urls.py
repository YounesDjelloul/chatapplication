from django.urls import path
from .views import *

urlpatterns = [
    path('posts/', PostsListView.as_view(), name='posts'),
    path('posts/<pk>/', PostDetailsView.as_view(), name='post_details'),
    path('posts/<pk>/likes/', PostLikesView.as_view(), name='post_likes'),
    path('posts/<pk>/comments/', PostCommentsView.as_view(), name='post_comments'),
    path('posts/<post_pk>/comments/<comment_pk>/', PostCommentDetailsView.as_view(), name='post_comment_details')
]