from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SimCard, Customer, Sale
from .serializers import SimCardSerializer, CustomerSerializer, SaleSerializer
from users.models import AuditLog
from inventory.models import PhoneNumber

class SimCardViewSet(viewsets.ModelViewSet):
    queryset = SimCard.objects.all().select_related('phone_number')
    serializer_class = SimCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['type', 'status']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Lista SIMs disponibles para la venta"""
        available_sims = self.queryset.filter(status='available')
        serializer = self.get_serializer(available_sims, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def migrate_to_esim(self, request, pk=None):
        """Migra una SIM física activa a una eSIM nueva"""
        old_sim = self.get_object()
        new_esim_id = request.data.get('new_esim_id')
        
        if not old_sim.phone_number:
            return Response({'error': 'La SIM original no tiene un número asignado'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_esim = SimCard.objects.get(id=new_esim_id, status='available', type='esim')
        except SimCard.DoesNotExist:
            return Response({'error': 'La eSIM seleccionada no está disponible'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Reflejar el cambio en los modelos
        phone = old_sim.phone_number
        
        # Desvincular de la vieja y marcar como desactivada
        old_sim.phone_number = None
        old_sim.status = 'deactivated'
        old_sim.save()
        
        # Vincular a la nueva y marcar como vendida (ya que es para un cliente existente)
        new_esim.phone_number = phone
        new_esim.status = 'sold'
        new_esim.save()
        
        # Si hay una venta previa vinculada a la SIM vieja, actualizarla (opcional, depende de la lógica de negocio)
        # Aquí simplemente notificamos el éxito
        
        AuditLog.objects.create(
            user=request.user,
            action='update',
            module='ventas',
            object_id=str(new_esim.id),
            description=f"Migró línea {phone.number} de SIM física ({old_sim.iccid}) a eSIM ({new_esim.iccid})"
        )
        
        return Response({'message': 'Migración completada exitosamente', 'new_esim': SimCardSerializer(new_esim).data})

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'dni', 'email']

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().select_related('customer', 'sim_card', 'seller')
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(seller=self.request.user)
        
        # Auditoría
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='ventas',
            object_id=str(instance.id),
            description=f"Realizó venta de SIM {instance.sim_card.iccid} a cliente {instance.customer.name} por ${instance.amount}"
        )

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Estadísticas rápidas de ventas"""
        from django.db.models import Sum, Count
        from django.utils import timezone
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        stats = {
            'total_sales_count': Sale.objects.count(),
            'total_sales_amount': Sale.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
            'month_sales_count': Sale.objects.filter(sale_date__gte=month_start).count(),
            'month_sales_amount': Sale.objects.filter(sale_date__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0,
            'sims_available': SimCard.objects.filter(status='available').count(),
            'esims_available': SimCard.objects.filter(status='available', type='esim').count(),
        }
        
        return Response(stats)
