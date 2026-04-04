from rest_framework import serializers
from .models import AccessLog, AnomalyAlert


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = ['id', 'card_id', 'door_name', 'access_granted', 'timestamp']
        read_only_fields = ['timestamp']


class AnomalyAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnomalyAlert
        fields = [
            'id', 'access_log', 'card_id', 'door_name',
            'rule', 'risk_level', 'description',
            'timestamp', 'resolved',
        ]
        read_only_fields = ['id', 'access_log', 'card_id', 'door_name',
                            'rule', 'risk_level', 'description', 'timestamp']