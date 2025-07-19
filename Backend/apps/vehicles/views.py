from rest_framework import viewsets
from .models import Vehicle
from .serializers import VehicleSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['registration_number', 'insurance_expiry_date', 'tax_expiry_date', 'permit_expiry_date']
    ordering_fields = ['registration_number', 'insurance_expiry_date', 'tax_expiry_date']
    ordering = ['registration_number']
