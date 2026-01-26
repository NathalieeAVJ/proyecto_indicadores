from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FolderViewSet, BusinessDocumentViewSet, DocumentVersionViewSet, DocumentPermissionViewSet

router = DefaultRouter()
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'documents', BusinessDocumentViewSet, basename='document')
router.register(r'versions', DocumentVersionViewSet, basename='document-version')
router.register(r'permissions', DocumentPermissionViewSet, basename='document-permission')

urlpatterns = [
    path('', include(router.urls)),
]
