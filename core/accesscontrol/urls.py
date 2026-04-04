from django.urls import path
from . import views

urlpatterns = [
    # Access logs
    path('api/logs/', views.AccessLogListCreateView.as_view(), name='accesslog-list'),
    path('api/logs/<int:pk>/', views.AccessLogDetailView.as_view(), name='accesslog-detail'),
    # Anomaly detection
    path('api/anomalies/', views.AnomalyAlertListView.as_view(), name='anomaly-list'),
    path('api/anomalies/stats/', views.AnomalyStatsView.as_view(), name='anomaly-stats'),
    path('api/anomalies/<int:pk>/resolve/', views.AnomalyAlertResolveView.as_view(), name='anomaly-resolve'),
]