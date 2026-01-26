from rest_framework import serializers
from django.contrib.auth import get_user_model
from rrhh.models import Employee

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'password', 'employee_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        employee_id = validated_data.pop('employee_id')
        user = User.objects.create_user(**validated_data)
        
        # Link to employee
        try:
            employee = Employee.objects.get(id=employee_id)
            employee.system_user = user
            employee.save()
        except Employee.DoesNotExist:
            user.delete()
            raise serializers.ValidationError({"employee_id": "El empleado seleccionado no existe."})
            
        return user
