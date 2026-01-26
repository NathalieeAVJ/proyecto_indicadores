from rest_framework import serializers
from .models import (
    PhoneNumber, RadioBase, 
    SparePartCategory, SparePart, SparePartUsage, 
    Budget, BudgetItem
)
from users.serializers import UserSerializer


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = '__all__'


class RadioBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioBase
        fields = '__all__'


# ==================== REPUESTOS ====================

class SparePartCategorySerializer(serializers.ModelSerializer):
    spare_parts_count = serializers.SerializerMethodField()

    class Meta:
        model = SparePartCategory
        fields = '__all__'
    
    def get_spare_parts_count(self, obj):
        return obj.spare_parts.count()


class SparePartSerializer(serializers.ModelSerializer):
    category_detail = SparePartCategorySerializer(source='category', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()

    class Meta:
        model = SparePart
        fields = '__all__'


class SparePartUsageSerializer(serializers.ModelSerializer):
    spare_part_detail = SparePartSerializer(source='spare_part', read_only=True)
    used_by_detail = UserSerializer(source='used_by', read_only=True)
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = SparePartUsage
        fields = '__all__'
        read_only_fields = ['unit_price_at_usage', 'used_by', 'used_at']


# ==================== PRESUPUESTOS ====================

class BudgetItemSerializer(serializers.ModelSerializer):
    spare_part_detail = SparePartSerializer(source='spare_part', read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = BudgetItem
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):
    items = BudgetItemSerializer(many=True, read_only=True)
    requested_by_detail = UserSerializer(source='requested_by', read_only=True)
    approved_by_detail = UserSerializer(source='approved_by', read_only=True)
    calculated_total = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['requested_by', 'approved_by', 'approved_amount']


class BudgetCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear presupuesto con sus items"""
    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Budget
        fields = ['title', 'description', 'requested_amount', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        budget = Budget.objects.create(**validated_data)
        
        for item in items_data:
            spare_part = SparePart.objects.get(id=item['spare_part'])
            BudgetItem.objects.create(
                budget=budget,
                spare_part=spare_part,
                quantity=item['quantity'],
                unit_price=item.get('unit_price', spare_part.unit_price)
            )
        
        return budget
