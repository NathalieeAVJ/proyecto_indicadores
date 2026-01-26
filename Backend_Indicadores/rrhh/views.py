from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Employee, Payroll, FamilyMember, Equipment, Absence, 
    Department, HRRequest, PerformanceEvaluation, MaintenanceLog
)
from .serializers import (
    EmployeeSerializer, PayrollSerializer, FamilyMemberSerializer, 
    EquipmentSerializer, AbsenceSerializer, DepartmentSerializer,
    HRRequestSerializer, PerformanceEvaluationSerializer, MaintenanceLogSerializer
)

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from incidencias.notifications import Notification
from users.models import AuditLog

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Start with the base queryset including select_related and prefetch_related
        queryset = Employee.objects.all().select_related('supervisor', 'system_user', 'department_ref').prefetch_related('family', 'equipment', 'absences')
        
        # Apply status filtering first
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        else:
            # Por defecto no mostrar los de lista negra en la vista principal de empleados
            queryset = queryset.exclude(status='blacklisted')

        user = self.request.user
        
        # System Admins see all (after status filter)
        if user.role == 'admin':
            return queryset
            
        profile = getattr(user, 'employee_profile', None)
        if not profile:
            # If no linked profile, they shouldn't see other employees
            return Employee.objects.none()
            
        # Presidente sees all
        if profile.rank == 0:
            return queryset
            
        # Others see: 
        # 1. Employees in their department AND ALL SUB-DEPARTMENTS with LOWER rank
        # 2. Their direct subordinates
        # 3. Themselves
        dept_ids = [profile.department_ref.id] if profile.department_ref else []
        if profile.department_ref:
            dept_ids.extend([d.id for d in profile.department_ref.get_descendants()])

        return queryset.filter(
            models.Q(department_ref_id__in=dept_ids, rank__gt=profile.rank) |
            models.Q(supervisor=profile) |
            models.Q(id=profile.id)
        ).distinct()

    @action(detail=True, methods=['post'])
    def blacklist(self, request, pk=None):
        employee = self.get_object()
        reason = request.data.get('reason', 'Sin motivo especificado')
        
        employee.status = 'blacklisted'
        employee.blacklist_reason = reason
        employee.blacklist_date = timezone.now().date()
        employee.save()
        
        if employee.system_user:
            user = employee.system_user
            user.is_active = False
            user.save()

        # Notificar a Auditoría
        User = get_user_model()
        auditors = User.objects.filter(role__in=['evaluator', 'admin'])
        for auditor in auditors:
            Notification.objects.create(
                user=auditor,
                title="Nueva Desincorporación / Lista Negra",
                message=f"El empleado {employee.first_name} {employee.last_name} ha sido movido a Lista Negra. Motivo: {reason}",
                link="/rrhh/blacklist"
            )

        # Registrar en AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='update',
            module='employees',
            object_id=str(employee.id),
            description=f"Movió a {employee.first_name} {employee.last_name} a LISTA NEGRA. Motivo: {reason}"
        )
            
        return Response({'status': 'employee blacklisted'})

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        employee = self.get_object()
        employee.status = 'active'
        employee.blacklist_reason = None
        employee.blacklist_date = None
        employee.save()
        
        # El usuario de sistema permanece desactivado por seguridad, 
        # debe ser reactivado manualmente si se desea restaurar el acceso.
        
        # Registrar en AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='update',
            module='employees',
            object_id=str(employee.id),
            description=f"Reincorporó al empleado {employee.first_name} {employee.last_name} desde Lista Negra."
        )
        
        return Response({'status': 'employee reactivated'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        employee = Employee.objects.filter(system_user=request.user).first()
        if not employee:
            return Response({'error': 'No profile linked'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(employee)
        return Response(serializer.data)

class FamilyMemberViewSet(viewsets.ModelViewSet):
    queryset = FamilyMember.objects.all()
    serializer_class = FamilyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().select_related('employee')
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='inventory_assets',
            object_id=str(instance.id),
            description=f"Registró nuevo activo de inventario: {instance.item_name} (Cod: {instance.internal_code})"
        )

class AbsenceViewSet(viewsets.ModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = [permissions.IsAuthenticated]

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all().select_related('employee')
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if month:
            queryset = queryset.filter(period_month=month)
        if year:
            queryset = queryset.filter(period_year=year)
            
        return queryset

    @action(detail=False, methods=['post'])
    def generate_month(self, request):
        month = request.data.get('month')
        year = request.data.get('year')
        
        if not month or not year:
            return Response({'error': 'Month and year required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get all active employees
        employees = Employee.objects.filter(status='active')
        count = 0
        
        for emp in employees:
            # Check if already exists
            if not Payroll.objects.filter(employee=emp, period_month=month, period_year=year).exists():
                Payroll.objects.create(
                    employee=emp,
                    period_month=month,
                    period_year=year,
                    base_salary=emp.base_salary,
                    payment_status='pending'
                )
                count += 1
                
        return Response({'message': f'Generated {count} payroll records'})

    @action(detail=False, methods=['post'])
    def bulk_pay(self, request):
        """Marca como pagada toda la nómina de un mes/año específico"""
        month = request.data.get('month')
        year = request.data.get('year')
        
        if not month or not year:
            return Response({'error': 'Month and year required'}, status=status.HTTP_400_BAD_REQUEST)
            
        updated = Payroll.objects.filter(
            period_month=month, 
            period_year=year, 
            payment_status='pending'
        ).update(
            payment_status='paid',
            payment_date=timezone.now().date()
        )
        
        AuditLog.objects.create(
            user=request.user,
            action='update',
            module='payroll',
            description=f"Emitió ORDEN DE PAGO para el periodo {month}/{year}. Registros actualizados: {updated}"
        )
        
        return Response({'message': f'Paid {updated} payroll records'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        employee = Employee.objects.filter(system_user=request.user).first()
        if not employee:
            return Response([], status=status.HTTP_200_OK)
        
        queryset = self.get_queryset().filter(employee=employee)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class HRRequestViewSet(viewsets.ModelViewSet):
    queryset = HRRequest.objects.all().select_related('employee', 'resolved_by')
    serializer_class = HRRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Admin ve todo
        if user.role == 'admin':
            return queryset
            
        profile = getattr(user, 'employee_profile', None)
        if not profile:
            return queryset.filter(employee__system_user=user)
            
        # Presidente ve todo
        if profile.rank == 0:
            return queryset
            
        # Filtro: Mis solicitudes O solicitudes de mis subordinados directos (pendiente aprobación)
        return queryset.filter(
            models.Q(employee=profile) | # Mías
            models.Q(employee__supervisor=profile) # De mi gente para aprobar
        ).distinct()

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'employee_profile', None)
        if profile:
            serializer.save(employee=profile)
        else:
            raise serializers.ValidationError("No tienes un perfil de empleado vinculado para realizar solicitudes.")

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if instance.employee.supervisor.system_user != request.user and request.user.role != 'admin':
            return Response({'error': 'No tienes permiso para aprobar esta solicitud'}, status=status.HTTP_403_FORBIDDEN)
            
        instance.status = 'approved'
        instance.supervisor_comment = request.data.get('comment', 'Aprobado por el supervisor.')
        instance.resolved_by = request.user
        instance.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        instance = self.get_object()
        if instance.employee.supervisor.system_user != request.user and request.user.role != 'admin':
            return Response({'error': 'No tienes permiso para rechazar esta solicitud'}, status=status.HTTP_403_FORBIDDEN)
            
        instance.status = 'rejected'
        instance.supervisor_comment = request.data.get('comment', 'Rechazado por el supervisor.')
        instance.resolved_by = request.user
        instance.save()
        return Response({'status': 'rejected'})

class PerformanceEvaluationViewSet(viewsets.ModelViewSet):
    queryset = PerformanceEvaluation.objects.all().select_related('employee', 'evaluated_by')
    serializer_class = PerformanceEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(evaluated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve_bonus(self, request, pk=None):
        evaluation = self.get_object()
        # Aquí se podría validar si el usuario tiene rango superior
        evaluation.bonus_approved = True
        evaluation.save()
        return Response({'status': 'bonus approved', 'amount': evaluation.suggested_bonus})

class MaintenanceLogViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['equipment']

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='maintenance_logs',
            object_id=str(instance.id),
            description=f"Registró mantenimiento {instance.get_type_display()} para {instance.equipment.item_name}. Costo: ${instance.cost}"
        )
