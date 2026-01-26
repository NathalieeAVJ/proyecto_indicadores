from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SimCardViewSet, CustomerViewSet, SaleViewSet

router = DefaultRouter()
router.register(r'sim-cards', SimCardViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'sales', SaleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
