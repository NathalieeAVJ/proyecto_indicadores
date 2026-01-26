from rest_framework import serializers
from .models import Incident, FailureType, RadioBaseIncident, IncidentAudit
class IncidentAuditSerializer(serializers.ModelSerializer):
    evaluator_name = serializers.CharField(source='evaluator.username', read_only=True)
    
    class Meta:
        model = IncidentAudit
        fields = '__all__'
        read_only_fields = ['evaluator', 'assignment_time_seconds', 'resolution_time_seconds', 'bonus_approved']

from users.serializers import UserSerializer
from inventory.serializers import PhoneNumberSerializer, RadioBaseSerializer

class FailureTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureType
        fields = '__all__'

class IncidentSerializer(serializers.ModelSerializer):
    # Read-only fields for detailed representation
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    phone_number_detail = PhoneNumberSerializer(source='phone_number', read_only=True)
    failure_type_detail = FailureTypeSerializer(source='failure_type', read_only=True)
    
    class Meta:
        model = Incident
        fields = '__all__'

class RadioBaseIncidentSerializer(serializers.ModelSerializer):
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    radio_base_detail = RadioBaseSerializer(source='radio_base', read_only=True)
    failure_type_detail = FailureTypeSerializer(source='failure_type', read_only=True)
    
    class Meta:
        model = RadioBaseIncident
        fields = '__all__'
