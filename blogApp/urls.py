from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_blog, name='create_blog'),
    path('list/', views.list_blogs, name='list_blogs'),
    path('update/<int:pk>/', views.update_blog, name='update_blog'),
    path('delete/<int:pk>/', views.delete_blog, name='delete_blog'),
    path('search/<str:email>/', views.search_blogs_by_user, name='search_blogs_by_user'),
]