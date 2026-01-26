from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Avg
from .models import Supplier, SupplierContact, Contract, PurchaseOrder, SupplierEvaluation
from .serializers import (
    SupplierSerializer, SupplierContactSerializer, ContractSerializer,
    PurchaseOrderSerializer, SupplierEvaluationSerializer
)
from users.models import AuditLog

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'status']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(rif__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='supplier',
            object_id=str(instance.id),
            description=f"Registró nuevo proveedor: {instance.name} ({instance.rif})"
        )
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Dashboard de estadísticas del proveedor"""
        supplier = self.get_object()
        
        data = {
            'supplier': self.get_serializer(supplier).data,
            'total_contracts': supplier.contracts.count(),
            'active_contracts': supplier.contracts.filter(status='active').count(),
            'total_value': supplier.contracts.aggregate(Sum('value'))['value__sum'] or 0,
            'purchase_orders': supplier.purchase_orders.count(),
            'avg_rating': supplier.rating,
            'evaluations_count': supplier.evaluation_count,
        }
        
        return Response(data)

class SupplierContactViewSet(viewsets.ModelViewSet):
    queryset = SupplierContact.objects.all()
    serializer_class = SupplierContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier']

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all().select_related('supplier', 'created_by')
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier', 'status']
    
    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='contract',
            object_id=str(instance.id),
            description=f"Creó contrato {instance.contract_number} con {instance.supplier.name} por ${instance.value}"
        )

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().select_related('supplier', 'contract', 'requested_by')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier', 'status', 'contract']
    
    def perform_create(self, serializer):
        instance = serializer.save(requested_by=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='purchase_order',
            object_id=str(instance.id),
            description=f"Creó orden de compra {instance.order_number} a {instance.supplier.name} por ${instance.total_amount}"
        )
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Aprobar orden de compra"""
        order = self.get_object()
        order.status = 'approved'
        order.save()
        
        AuditLog.objects.create(
            user=request.user,
            action='update',
            module='purchase_order',
            object_id=str(order.id),
            description=f"Aprobó orden de compra {order.order_number}"
        )
        
        return Response(self.get_serializer(order).data)
    
    @action(detail=True, methods=['patch'])
    def receive(self, request, pk=None):
        """Marcar orden como recibida"""
        order = self.get_object()
        order.status = 'received'
        order.save()
        
        AuditLog.objects.create(
            user=request.user,
            action='update',
            module='purchase_order',
            object_id=str(order.id),
            description=f"Recibió orden de compra {order.order_number}"
        )
        
        return Response(self.get_serializer(order).data)

class SupplierEvaluationViewSet(viewsets.ModelViewSet):
    queryset = SupplierEvaluation.objects.all().select_related('supplier', 'contract', 'evaluator')
    serializer_class = SupplierEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['supplier', 'contract']
    
    def perform_create(self, serializer):
        instance = serializer.save(evaluator=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='supplier_evaluation',
            object_id=str(instance.id),
            description=f"Evaluó proveedor {instance.supplier.name} con calificación {instance.overall_score}"
        )
