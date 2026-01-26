from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, FuelLogViewSet, VehicleMaintenanceViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'fuel-logs', FuelLogViewSet)
router.register(r'maintenances', VehicleMaintenanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
