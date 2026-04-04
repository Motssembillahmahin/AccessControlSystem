from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccessLog, AnomalyAlert
from .serializers import AccessLogSerializer, AnomalyAlertSerializer


class AccessLogListCreateView(generics.ListCreateAPIView):
    queryset = AccessLog.objects.all().order_by('-timestamp')
    serializer_class = AccessLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['card_id', 'door_name', 'access_granted']
    search_fields = ['card_id', 'door_name']


class AccessLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer


class AnomalyAlertListView(generics.ListAPIView):
    """List all anomaly alerts, newest first. Filterable by card, rule, risk, resolved."""
    queryset = AnomalyAlert.objects.all().order_by('-timestamp')
    serializer_class = AnomalyAlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['card_id', 'door_name', 'rule', 'risk_level', 'resolved']
    search_fields = ['card_id', 'door_name', 'description']


class AnomalyAlertResolveView(APIView):
    """Mark a specific anomaly alert as resolved."""

    def patch(self, request, pk):
        try:
            alert = AnomalyAlert.objects.get(pk=pk)
        except AnomalyAlert.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        alert.resolved = True
        alert.save()
        return Response(AnomalyAlertSerializer(alert).data)


class AnomalyStatsView(APIView):
    """Aggregated anomaly statistics — totals by risk level, rule, and top risky cards."""

    def get(self, request):
        total = AnomalyAlert.objects.count()
        unresolved = AnomalyAlert.objects.filter(resolved=False).count()

        by_risk = dict(
            AnomalyAlert.objects
            .values('risk_level')
            .annotate(count=Count('id'))
            .values_list('risk_level', 'count')
        )
        by_rule = dict(
            AnomalyAlert.objects
            .values('rule')
            .annotate(count=Count('id'))
            .values_list('rule', 'count')
        )
        top_cards = list(
            AnomalyAlert.objects
            .filter(resolved=False)
            .values('card_id')
            .annotate(alert_count=Count('id'))
            .order_by('-alert_count')[:5]
        )

        return Response({
            'total_alerts': total,
            'unresolved_alerts': unresolved,
            'by_risk_level': by_risk,
            'by_rule': by_rule,
            'top_risky_cards': top_cards,
        })