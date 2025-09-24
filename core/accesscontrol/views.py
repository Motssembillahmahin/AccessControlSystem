from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import AccessLog
from .serializers import AccessLogSerializer

class AccessLogListCreateView(generics.ListCreateAPIView):
    queryset = AccessLog.objects.all().order_by('-timestamp')
    serializer_class = AccessLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['card_id', 'door_name', 'access_granted']
    search_fields = ['card_id', 'door_name']

class AccessLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer