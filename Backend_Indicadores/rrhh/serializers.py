from rest_framework import serializers
from .models import Employee, Payroll, FamilyMember, Equipment, Absence

class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

class AbsenceSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = Absence
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    family = FamilyMemberSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    absences = AbsenceSerializer(many=True, read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.first_name', read_only=True)
    system_user_name = serializers.CharField(source='system_user.username', read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

class PayrollSerializer(serializers.ModelSerializer):
    employee_detail = EmployeeSerializer(source='employee', read_only=True)

    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['net_salary']
