from rest_framework import serializers
from .models import Supplier, SupplierContact, Contract, PurchaseOrder, SupplierEvaluation

class SupplierContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierContact
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    # Contactos anidados
    contacts = SupplierContactSerializer(many=True, read_only=True)
    
    # Estadísticas
    active_contracts_count = serializers.SerializerMethodField()
    total_contracts_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = '__all__'
    
    def get_active_contracts_count(self, obj):
        return obj.contracts.filter(status='active').count()
    
    def get_total_contracts_value(self, obj):
        from django.db.models import Sum
        result = obj.contracts.filter(status='active').aggregate(Sum('value'))
        return result['value__sum'] or 0

class ContractSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Contract
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    contract_number = serializers.CharField(source='contract.contract_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class SupplierEvaluationSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.username', read_only=True)
    
    class Meta:
        model = SupplierEvaluation
        fields = '__all__'
        read_only_fields = ['overall_score']  # Se calcula automáticamente
