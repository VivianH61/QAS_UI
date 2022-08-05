from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView
)
from . import views
from .views import *
from django.urls import reverse

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('transaction/', views.transaction, name='blog-transaction'),
    path('setting/', views.setting, name='blog-setting'),
    path('sent_emails/', views.sent_emails, name='sent-emails'),
    path('enter_share/', views.enter_share, name='enter-share'),
]


