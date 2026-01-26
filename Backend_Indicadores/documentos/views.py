from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Folder, BusinessDocument, DocumentVersion, DocumentPermission
from .serializers import FolderSerializer, BusinessDocumentSerializer, DocumentVersionSerializer, DocumentPermissionSerializer
from users.models import AuditLog

class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        parent_id = self.request.query_params.get('parent', None)
        
        if parent_id == 'null' or parent_id == '':
            # Carpetas raíz
            return queryset.filter(parent__isnull=True)
        elif parent_id:
            return queryset.filter(parent_id=parent_id)
        
        return queryset
    
    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='document_folder',
            object_id=str(instance.id),
            description=f"Creó carpeta: {instance.get_full_path()}"
        )
    
    @action(detail=True, methods=['get'])
    def tree(self, request, pk=None):
        """Obtiene el árbol completo de subcarpetas"""
        folder = self.get_object()
        subfolders = folder.subfolders.all()
        serializer = self.get_serializer(subfolders, many=True)
        return Response(serializer.data)

class BusinessDocumentViewSet(viewsets.ModelViewSet):
    queryset = BusinessDocument.objects.all().select_related('folder', 'uploaded_by', 'employee', 'radiobase')
    serializer_class = BusinessDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'folder']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        instance = serializer.save(uploaded_by=self.request.user, version_number=1)
        
        # Crear la primera versión
        DocumentVersion.objects.create(
            document=instance,
            version_number=1,
            file=instance.file,
            uploaded_by=self.request.user,
            notes="Versión inicial"
        )
        
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='business_document',
            object_id=str(instance.id),
            description=f"Subió documento: {instance.title} ({instance.get_category_display()})"
        )
    
    @action(detail=True, methods=['post'])
    def upload_version(self, request, pk=None):
        """Sube una nueva versión del documento"""
        document = self.get_object()
        file = request.FILES.get('file')
        notes = request.data.get('notes', '')
        
        if not file:
            return Response({'error': 'No se proporcionó archivo'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Incrementar versión
        document.version_number += 1
        document.file = file
        document.save()
        
        # Crear registro de versión
        version = DocumentVersion.objects.create(
            document=document,
            version_number=document.version_number,
            file=file,
            uploaded_by=request.user,
            notes=notes,
            file_size=file.size if hasattr(file, 'size') else None
        )
        
        AuditLog.objects.create(
            user=request.user,
            action='update',
            module='business_document',
            object_id=str(document.id),
            description=f"Subió nueva versión v{document.version_number} de: {document.title}"
        )
        
        return Response(DocumentVersionSerializer(version).data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Descarga el documento"""
        document = self.get_object()
        
        AuditLog.objects.create(
            user=request.user,
            action='view',
            module='business_document',
            object_id=str(document.id),
            description=f"Descargó documento: {document.title}"
        )
        
        # En producción, aquí iría la lógica de descarga
        return Response({'file_url': document.file.url if document.file else None})

class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentVersion.objects.all().select_related('document', 'uploaded_by')
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['document']

class DocumentPermissionViewSet(viewsets.ModelViewSet):
    queryset = DocumentPermission.objects.all().select_related('user', 'document', 'folder')
    serializer_class = DocumentPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        instance = serializer.save(granted_by=self.request.user)
        target = instance.document or instance.folder
        subject = instance.user or f"Rol {instance.role}"
        
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='document_permission',
            object_id=str(instance.id),
            description=f"Otorgó permiso '{instance.get_permission_level_display()}' a {subject} en {target}"
        )
