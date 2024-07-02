from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_feedback, name='create_feedback'),
    path('list/', views.list_feedbacks, name='list_feedbacks'),
    path('update/<int:pk>/', views.update_feedback, name='update_feedback'),
    path('delete/<int:pk>/', views.delete_feedback, name='delete_feedback'),
    path('search/feedback/', views.search_feedback_by_content, name='search_feedback_by_content'),
    path('search/request/', views.search_feedback_by_request, name='search_feedback_by_request'),
    path('search/email/', views.search_feedback_by_email, name='search_feedback_by_email'),
    path('feedback/<int:pk>/', views.get_feedback_by_id, name='get_feedback_by_id'),
    path('respond/<int:pk>/', views.respond_feedback, name='respond_feedback'),
    path('download/pdf/', views.download_feedbacks_pdf, name='download_feedbacks_pdf'),  # New route for PDF download
    path('download/excel/', views.download_feedbacks_excel, name='download_feedbacks_excel'),  # New route for Excel download

]
