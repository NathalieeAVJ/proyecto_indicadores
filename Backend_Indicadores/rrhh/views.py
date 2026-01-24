from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Employee, Payroll, FamilyMember, Equipment, Absence
from .serializers import (
    EmployeeSerializer, PayrollSerializer, 
    FamilyMemberSerializer, EquipmentSerializer, AbsenceSerializer
)

from django.db import models

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Employee.objects.all().prefetch_related('family', 'equipment', 'absences')
        user = self.request.user
        
        # System Admins see all
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
        # 1. Employees in their department with LOWER rank (Higher number)
        # 2. Their direct subordinates (even if in different departments)
        # 3. Themselves
        return queryset.filter(
            models.Q(department=profile.department, rank__gt=profile.rank) |
            models.Q(supervisor=profile) |
            models.Q(id=profile.id)
        ).distinct()

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
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

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

    @action(detail=False, methods=['get'])
    def me(self, request):
        employee = Employee.objects.filter(system_user=request.user).first()
        if not employee:
            return Response([], status=status.HTTP_200_OK)
        
        queryset = self.get_queryset().filter(employee=employee)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
