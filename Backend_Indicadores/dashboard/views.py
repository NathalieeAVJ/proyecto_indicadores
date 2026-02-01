from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Sum, Q, Count, F
from django.db import models
from django.utils import timezone

from incidencias.models import Incident, RadioBaseIncident
from ventas.models import Sale
from inventory.models import SparePart

class DashboardStatsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. INCIDENCIAS PENDIENTES
        # Sumamos incidencias de telefonos + radiobases que no estén resueltas
        pending_incidents = Incident.objects.filter(
            Q(status='pending') | Q(status='in_review')
        ).count()
        
        pending_rb_incidents = RadioBaseIncident.objects.filter(
            Q(status='pending') | Q(status='in_review')
        ).count()
        
        total_open_incidents = pending_incidents + pending_rb_incidents

        # 2. VENTAS DEL MES ACTUAL
        now = timezone.now()
        current_month_sales = Sale.objects.filter(
            sale_date__year=now.year,
            sale_date__month=now.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 3. STOCK BAJO (Alertas)
        # Repuestos donde la cantidad actual es menor o igual al minimo permitido
        low_stock_count = SparePart.objects.filter(
            quantity_in_stock__lte=models.F('minimum_stock')
        ).count()

        return Response({
            'incidents_open': total_open_incidents,
            'monthly_sales': current_month_sales,
            'low_stock_items': low_stock_count,
            'timestamp': now
        })
