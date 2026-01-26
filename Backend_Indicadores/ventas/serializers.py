from rest_framework import serializers
from .models import SimCard, Customer, Sale
from inventory.serializers import PhoneNumberSerializer

class SimCardSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    phone_number_detail = PhoneNumberSerializer(source='phone_number', read_only=True)
    
    class Meta:
        model = SimCard
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    sim_card_iccid = serializers.CharField(source='sim_card.iccid', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    # Detail for nested reading
    customer_detail = CustomerSerializer(source='customer', read_only=True)
    sim_card_detail = SimCardSerializer(source='sim_card', read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ['seller', 'sale_date']
