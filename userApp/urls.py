from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('users/', views.view_all_users, name='view_all_users'),
    path('user_edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    

    path('total_users/', views.total_users, name='total_users'),
    path('all_users/', views.all_users, name='all_users'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('get_user/<int:user_id>/', views.get_user_by_id, name='get_user_by_id'),
    path('create_user/', views.create_user, name='create_user'),
    
    path('download/pdf/', views.download_users_pdf, name='download_feedbacks_pdf'),  # New route for PDF download
    path('download/excel/', views.download_users_excel, name='download_feedbacks_excel'),  # New route for Excel download
]
