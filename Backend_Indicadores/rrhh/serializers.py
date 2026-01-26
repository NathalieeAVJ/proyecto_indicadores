from rest_framework import serializers
from .models import (
    Employee, Payroll, FamilyMember, Equipment, 
    Absence, Department, HRRequest, PerformanceEvaluation,
    MaintenanceLog
)

class HRRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.first_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    equipment_name = serializers.CharField(source='equipment.item_name', read_only=True)
    equipment_code = serializers.CharField(source='equipment.internal_code', read_only=True)
    
    class Meta:
        model = HRRequest
        fields = '__all__'

class PerformanceEvaluationSerializer(serializers.ModelSerializer):
    evaluated_by_name = serializers.CharField(source='evaluated_by.username', read_only=True)
    
    class Meta:
        model = PerformanceEvaluation
        fields = '__all__'
        read_only_fields = ['evaluated_by', 'bonus_approved']

class DepartmentSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    manager_detail = serializers.SerializerMethodField()
    staff_count = serializers.IntegerField(source='employees.count', read_only=True)
    staff_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'

    def get_manager_detail(self, obj):
        # El encargado es el empleado del departamento con menor rank (0 es presidente, 3 es gerente)
        manager = obj.employees.order_by('rank').first()
        if manager:
            return {
                'id': manager.id,
                'full_name': f"{manager.first_name} {manager.last_name}",
                'position': manager.position,
                'rank': manager.rank
            }
        return None

    def get_staff_list(self, obj):
        # Lista simplificada para el modal del organigrama
        return [
            {
                'id': emp.id,
                'full_name': f"{emp.first_name} {emp.last_name}",
                'position': emp.position,
                'status': emp.status
            } for emp in obj.employees.all()
        ]

class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.first_name', read_only=True)
    
    class Meta:
        model = Equipment
        fields = '__all__'

class MaintenanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceLog
        fields = '__all__'

class AbsenceSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = Absence
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    family = FamilyMemberSerializer(many=True, read_only=True)
    equipment = EquipmentSerializer(many=True, read_only=True)
    maintenance_history = MaintenanceLogSerializer(many=True, read_only=True, source='equipment.maintenance_logs') # Opcional si se requiere ver desde emp
    absences = AbsenceSerializer(many=True, read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.first_name', read_only=True)
    system_user_name = serializers.CharField(source='system_user.username', read_only=True)
    department_detail = DepartmentSerializer(source='department_ref', read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

class PayrollSerializer(serializers.ModelSerializer):
    employee_detail = EmployeeSerializer(source='employee', read_only=True)

    class Meta:
        model = Payroll
        fields = '__all__'
        read_only_fields = ['net_salary']
