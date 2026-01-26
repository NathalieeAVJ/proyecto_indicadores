from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, SupplierContactViewSet, ContractViewSet,
    PurchaseOrderViewSet, SupplierEvaluationViewSet
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'contacts', SupplierContactViewSet, basename='contact')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'evaluations', SupplierEvaluationViewSet, basename='evaluation')

urlpatterns = [
    path('', include(router.urls)),
]
