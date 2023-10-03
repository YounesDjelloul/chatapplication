from django.urls import path
from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='obtain_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),

    path('', AccountsListView.as_view(), name='accounts'),
    path('me/', AccountDetailView.as_view(), name='account_detail'),

    path('profiles/<pk>/', ProfileDetailView.as_view(), name='profile_detail'),

    path('likes/', LikesListView.as_view(), name='likes'),
    path('likes/<pk>/', LikesDetailView.as_view(), name='like_detail'),
]