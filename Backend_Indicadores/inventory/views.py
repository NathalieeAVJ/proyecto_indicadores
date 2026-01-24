from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Sum, F

from .models import (
    PhoneNumber, RadioBase,
    SparePartCategory, SparePart, SparePartUsage,
    Budget, BudgetItem
)
from .serializers import (
    PhoneNumberSerializer, RadioBaseSerializer,
    SparePartCategorySerializer, SparePartSerializer, SparePartUsageSerializer,
    BudgetSerializer, BudgetCreateSerializer, BudgetItemSerializer
)


class PhoneNumberViewSet(viewsets.ModelViewSet):
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = [permissions.IsAuthenticated]


class RadioBaseViewSet(viewsets.ModelViewSet):
    queryset = RadioBase.objects.all()
    serializer_class = RadioBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Datos para el mapa de radiobases"""
        radiobases = RadioBase.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False
        ).values('id', 'name', 'code', 'location', 'latitude', 'longitude')
        return Response(list(radiobases))


# ==================== REPUESTOS ====================

class SparePartCategoryViewSet(viewsets.ModelViewSet):
    queryset = SparePartCategory.objects.all()
    serializer_class = SparePartCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class SparePartViewSet(viewsets.ModelViewSet):
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SparePart.objects.all()
        
        # Filtrar por categoría
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filtrar solo stock bajo
        low_stock = self.request.query_params.get('low_stock')
        if low_stock and low_stock.lower() == 'true':
            queryset = queryset.filter(quantity_in_stock__lte=F('minimum_stock'))
        
        # Búsqueda por nombre o código
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | models.Q(code__icontains=search)
            )
        
        return queryset

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """Agregar stock a un repuesto"""
        spare_part = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        if quantity <= 0:
            return Response(
                {'error': 'La cantidad debe ser mayor a 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        spare_part.quantity_in_stock += quantity
        spare_part.save()
        
        return Response({
            'message': f'Stock actualizado. Nuevo stock: {spare_part.quantity_in_stock}',
            'new_stock': spare_part.quantity_in_stock
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas del inventario"""
        total_items = SparePart.objects.count()
        low_stock_count = SparePart.objects.filter(
            quantity_in_stock__lte=F('minimum_stock')
        ).count()
        total_value = SparePart.objects.aggregate(
            total=Sum(F('quantity_in_stock') * F('unit_price'))
        )['total'] or 0
        
        return Response({
            'total_items': total_items,
            'low_stock_count': low_stock_count,
            'total_inventory_value': float(total_value)
        })


class SparePartUsageViewSet(viewsets.ModelViewSet):
    queryset = SparePartUsage.objects.all()
    serializer_class = SparePartUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SparePartUsage.objects.all()
        
        # Filtrar por tipo de incidencia
        incident_type = self.request.query_params.get('incident_type')
        if incident_type:
            queryset = queryset.filter(incident_type=incident_type)
        
        # Filtrar por ID de incidencia
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(incident_id=incident_id)
        
        # Filtrar por repuesto
        spare_part = self.request.query_params.get('spare_part')
        if spare_part:
            queryset = queryset.filter(spare_part_id=spare_part)
        
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        spare_part = SparePart.objects.select_for_update().get(
            id=self.request.data.get('spare_part')
        )
        quantity = int(self.request.data.get('quantity_used', 0))
        
        # Validar stock disponible
        if spare_part.quantity_in_stock < quantity:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'quantity_used': f'Stock insuficiente. Disponible: {spare_part.quantity_in_stock}'
            })
        
        # Descontar del inventario
        spare_part.quantity_in_stock -= quantity
        spare_part.save()
        
        # Guardar el uso con precio actual
        serializer.save(
            used_by=self.request.user,
            unit_price_at_usage=spare_part.unit_price
        )


# ==================== PRESUPUESTOS ====================

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return BudgetCreateSerializer
        return BudgetSerializer

    def get_queryset(self):
        queryset = Budget.objects.prefetch_related('items', 'items__spare_part').all()
        
        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrar por usuario (solo sus presupuestos)
        user = self.request.user
        if user.role != 'admin':
            queryset = queryset.filter(requested_by=user)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Enviar presupuesto para aprobación"""
        budget = self.get_object()
        
        if budget.status != 'draft':
            return Response(
                {'error': 'Solo presupuestos en borrador pueden ser enviados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        budget.status = 'pending'
        budget.save()
        
        return Response({'message': 'Presupuesto enviado para aprobación'})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprobar presupuesto (solo admin)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Solo administradores pueden aprobar presupuestos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        budget = self.get_object()
        
        if budget.status != 'pending':
            return Response(
                {'error': 'Solo presupuestos pendientes pueden ser aprobados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approved_amount = request.data.get('approved_amount', budget.requested_amount)
        approval_notes = request.data.get('approval_notes', '')
        
        budget.status = 'approved'
        budget.approved_by = request.user
        budget.approved_amount = approved_amount
        budget.approval_notes = approval_notes
        budget.save()
        
        return Response({'message': 'Presupuesto aprobado'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechazar presupuesto (solo admin)"""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Solo administradores pueden rechazar presupuestos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        budget = self.get_object()
        
        if budget.status != 'pending':
            return Response(
                {'error': 'Solo presupuestos pendientes pueden ser rechazados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        budget.status = 'rejected'
        budget.approved_by = request.user
        budget.approval_notes = request.data.get('rejection_reason', '')
        budget.save()
        
        return Response({'message': 'Presupuesto rechazado'})

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def execute(self, request, pk=None):
        """Ejecutar presupuesto aprobado - agregar stock"""
        budget = self.get_object()
        
        if budget.status != 'approved':
            return Response(
                {'error': 'Solo presupuestos aprobados pueden ser ejecutados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Agregar los items al inventario
        for item in budget.items.all():
            spare_part = SparePart.objects.select_for_update().get(id=item.spare_part_id)
            spare_part.quantity_in_stock += item.quantity
            spare_part.save()
        
        budget.status = 'executed'
        budget.save()
        
        return Response({'message': 'Presupuesto ejecutado. Stock actualizado.'})


class BudgetItemViewSet(viewsets.ModelViewSet):
    queryset = BudgetItem.objects.all()
    serializer_class = BudgetItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = BudgetItem.objects.all()
        budget = self.request.query_params.get('budget')
        if budget:
            queryset = queryset.filter(budget_id=budget)
        return queryset
