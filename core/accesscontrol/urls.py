from django.urls import path
from . import views

urlpatterns = [
    path('api/logs/', views.AccessLogListCreateView.as_view(), name='accesslog-list'),
    path('api/logs/<int:pk>/', views.AccessLogDetailView.as_view(), name='accesslog-detail'),
]