from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from users.views import UserViewSet
from inventory.views import (
    PhoneNumberViewSet, RadioBaseViewSet,
    SparePartCategoryViewSet, SparePartViewSet, SparePartUsageViewSet,
    BudgetViewSet, BudgetItemViewSet
)
from incidencias.views import IncidentViewSet, FailureTypeViewSet, RadioBaseIncidentViewSet, IncidentAuditViewSet
from rrhh.views import (
    EmployeeViewSet, PayrollViewSet, FamilyMemberViewSet, 
    EquipmentViewSet, AbsenceViewSet, DepartmentViewSet,
    HRRequestViewSet, PerformanceEvaluationViewSet, MaintenanceLogViewSet
)
from incidencias.notification_views import NotificationViewSet
from incidencias.work_order_views import WorkOrderViewSet
from users.audit_views import AuditLogViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'audit-logs', AuditLogViewSet)
router.register(r'phones', PhoneNumberViewSet)
router.register(r'radio-bases', RadioBaseViewSet)
router.register(r'incidents', IncidentViewSet)
router.register(r'incident-audits', IncidentAuditViewSet)
router.register(r'rb-incidents', RadioBaseIncidentViewSet)
router.register(r'failure-types', FailureTypeViewSet)
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'payroll', PayrollViewSet, basename='payroll')
router.register(r'family-members', FamilyMemberViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'absences', AbsenceViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'hr-requests', HRRequestViewSet)
router.register(r'evaluations', PerformanceEvaluationViewSet)
router.register(r'maintenance-logs', MaintenanceLogViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'work-orders', WorkOrderViewSet)

# Inventario de Repuestos y Presupuestos
router.register(r'spare-part-categories', SparePartCategoryViewSet)
router.register(r'spare-parts', SparePartViewSet)
router.register(r'spare-part-usage', SparePartUsageViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'budget-items', BudgetItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token),
    path('api/v1/', include(router.urls)),
    path('api/v1/logistica/', include('logistica.urls')),
    path('api/v1/wiki/', include('wiki.urls')),
    path('api/v1/documentos/', include('documentos.urls')),
    path('api/v1/procura/', include('procura.urls')),
    path('api/v1/ventas/', include('ventas.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]
