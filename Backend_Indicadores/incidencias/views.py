from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, F
from .models import Incident, FailureType, RadioBaseIncident, IncidentAudit
from .serializers import (
    IncidentSerializer, FailureTypeSerializer, 
    RadioBaseIncidentSerializer, IncidentAuditSerializer
)
from rrhh.models import Employee

class FailureTypeViewSet(viewsets.ModelViewSet):
    queryset = FailureType.objects.all()
    serializer_class = FailureTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Incident.objects.all()
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            queryset = queryset.filter(start_date__gte=start)
        if end:
            queryset = queryset.filter(start_date__lte=end)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        # Phone Incidents Stats
        qs_phone = self.get_queryset()
        
        # RadioBase Incidents Stats
        qs_rb = RadioBaseIncident.objects.all()
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if start: qs_rb = qs_rb.filter(start_date__gte=start)
        if end: qs_rb = qs_rb.filter(start_date__lte=end)

        def get_stats(qs):
            total = qs.count()
            by_status = qs.values('status').annotate(count=Count('status'))
            by_type = qs.values('failure_type__name').annotate(count=Count('failure_type'))
            
            # KPI 1: Tiempo de Asignación (Desde creación hasta asignación)
            assigned = qs.filter(assigned_at__isnull=False)
            avg_assign = assigned.aggregate(avg=Avg(F('assigned_at') - F('created_at')))['avg']
            
            # KPI 2: Tiempo de Resolución (Desde asignación hasta cierre)
            resolved = qs.filter(status='solved', solved_date__isnull=False, assigned_at__isnull=False)
            avg_res = resolved.aggregate(avg=Avg(F('solved_date') - F('assigned_at')))['avg']
            
            # Desglose por Técnico con Nombres Reales e ID de Empleado
            tech_performance = resolved.values(
                'assigned_to__employee_profile__id',
                'assigned_to__first_name',
                'assigned_to__last_name'
            ).annotate(
                avg_time=Avg(F('solved_date') - F('assigned_at')),
                total_solved=Count('id')
            )

            return {
                'total': total,
                'by_status': by_status,
                'by_type': by_type,
                'avg_assignment_time': abs(avg_assign.total_seconds()) if avg_assign else None,
                'avg_resolution_time': abs(avg_res.total_seconds()) if avg_res else None,
                'technician_performance': [
                    {
                        'id': tp['assigned_to__employee_profile__id'],
                        'full_name': f"{tp['assigned_to__first_name']} {tp['assigned_to__last_name']}",
                        'avg_seconds': abs(tp['avg_time'].total_seconds()) if tp['avg_time'] else 0,
                        'total_solved': tp['total_solved']
                    } for tp in tech_performance
                ]
            }
        
        # RRHH Stats
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status='active').count()

        return Response({
            'phone': get_stats(qs_phone),
            'radiobase': get_stats(qs_rb),
            'rrhh': {
                'total_employees': total_employees,
                'active_employees': active_employees,
            },
            'summary': {
                'total_general_incidents': qs_phone.count() + qs_rb.count()
            }
        })

class RadioBaseIncidentViewSet(viewsets.ModelViewSet):
    queryset = RadioBaseIncident.objects.all()
    serializer_class = RadioBaseIncidentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RadioBaseIncident.objects.all()
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            queryset = queryset.filter(start_date__gte=start)
        if end:
            queryset = queryset.filter(start_date__lte=end)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class IncidentAuditViewSet(viewsets.ModelViewSet):
    queryset = IncidentAudit.objects.all().select_related('incident', 'evaluator')
    serializer_class = IncidentAuditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        incident = serializer.validated_data['incident']
        # Calcular tiempos al vuelo para el snapshot de auditoría
        assign_time = (incident.assigned_at - incident.start_date).total_seconds() if incident.assigned_at else None
        res_time = (incident.solved_date - incident.assigned_at).total_seconds() if incident.solved_date and incident.assigned_at else None
        
        serializer.save(
            evaluator=self.request.user,
            assignment_time_seconds=int(assign_time) if assign_time else None,
            resolution_time_seconds=int(res_time) if res_time else None
        )

    @action(detail=True, methods=['post'])
    def approve_bonus(self, request, pk=None):
        audit = self.get_object()
        audit.bonus_approved = True
        audit.save()
        return Response({'status': 'bonus approved', 'amount': audit.suggested_bonus})
