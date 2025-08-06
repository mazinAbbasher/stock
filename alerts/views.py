from django.shortcuts import render
from rest_framework import generics, permissions, filters
from .models import Alert
from .serializers import AlertSerializer

class AlertListCreateView(generics.ListCreateAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [filters.OrderingFilter]
    # ordering_fields = ['created_at', 'triggered_at']
    # ordering = ['-created_at']

    def get_queryset(self):
        queryset = Alert.objects.filter(user=self.request.user)
        triggered = self.request.query_params.get('triggered')
        if triggered is not None:
            queryset = queryset.filter(triggered=triggered.lower() == 'true')
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AlertDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
