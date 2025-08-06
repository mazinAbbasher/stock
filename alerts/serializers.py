from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            'id', 'symbol', 'alert_type', 'condition', 'target_price',
            'duration_minutes', 'created_at', 'triggered', 'triggered_at'
        ]
        read_only_fields = ['created_at', 'triggered', 'triggered_at']

    def validate(self, attrs):
        alert_type = attrs.get('alert_type')
        duration_minutes = attrs.get('duration_minutes')
        if alert_type == 'duration' and not duration_minutes:
            raise serializers.ValidationError({'duration_minutes': 'This field is required for duration alerts.'})
        return attrs
