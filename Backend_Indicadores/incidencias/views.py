from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, F
from .models import Incident, FailureType, RadioBaseIncident
from .serializers import IncidentSerializer, FailureTypeSerializer, RadioBaseIncidentSerializer
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
            resolved = qs.filter(status='solved', solved_date__isnull=False, start_date__isnull=False)
            avg_time = resolved.aggregate(avg=Avg(F('solved_date') - F('start_date')))['avg']
            return {
                'total': total,
                'by_status': by_status,
                'by_type': by_type,
                'avg_resolution_time': avg_time.total_seconds() if avg_time else None
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
