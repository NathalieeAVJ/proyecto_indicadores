from rest_framework import serializers
from .models import Vehicle, FuelLog, VehicleMaintenance

class VehicleSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Vehicle
        fields = '__all__'

class FuelLogSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    class Meta:
        model = FuelLog
        fields = '__all__'

class VehicleMaintenanceSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    class Meta:
        model = VehicleMaintenance
        fields = '__all__'
