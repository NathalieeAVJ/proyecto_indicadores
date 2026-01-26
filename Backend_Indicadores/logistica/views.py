from rest_framework import viewsets, permissions
from .models import Vehicle, FuelLog, VehicleMaintenance
from .serializers import VehicleSerializer, FuelLogSerializer, VehicleMaintenanceSerializer
from users.models import AuditLog

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='fleet_vehicle',
            object_id=str(instance.id),
            description=f"Registró nuevo vehículo de flota: {instance.brand} {instance.model} ({instance.plate})"
        )

class FuelLogViewSet(viewsets.ModelViewSet):
    queryset = FuelLog.objects.all().select_related('vehicle')
    serializer_class = FuelLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vehicle']

    def perform_create(self, serializer):
        instance = serializer.save()
        # Actualizar odómetro del vehículo automáticamente
        vehicle = instance.vehicle
        if instance.odometer_reading > vehicle.odometer:
            vehicle.odometer = instance.odometer_reading
            vehicle.save()
            
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='fleet_fuel',
            object_id=str(instance.id),
            description=f"Registró carga de combustible: {instance.liters}L para {instance.vehicle.plate}. Costo: ${instance.cost_total}"
        )

class VehicleMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = VehicleMaintenance.objects.all().select_related('vehicle')
    serializer_class = VehicleMaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vehicle']

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='fleet_maintenance',
            object_id=str(instance.id),
            description=f"Registró mantenimiento {instance.get_type_display()} para vehículo {instance.vehicle.plate}. Costo: ${instance.cost}"
        )
