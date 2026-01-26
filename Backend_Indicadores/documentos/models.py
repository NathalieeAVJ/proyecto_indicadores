from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from rrhh.models import Employee
from inventory.models import RadioBase

User = get_user_model()

class Folder(models.Model):
    """Carpeta para organizar documentos de forma jerárquica"""
    name = models.CharField(max_length=100, verbose_name="Nombre de la Carpeta")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders', verbose_name="Carpeta Padre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, default='mdi-folder', verbose_name="Icono MDI")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} / {self.name}"
        return self.name
    
    def get_full_path(self):
        """Obtiene la ruta completa de la carpeta"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " / ".join(path)
    
    class Meta:
        verbose_name = "Carpeta"
        verbose_name_plural = "Carpetas"
        ordering = ['name']
        unique_together = ['parent', 'name']

class BusinessDocument(models.Model):
    CAT_CHOICES = [
        ('contract', 'Contrato / Legal'),
        ('invoice', 'Factura / Comprobante'),
        ('blueprint', 'Plano / Técnico'),
        ('id_card', 'Documento Identidad'),
        ('certificate', 'Certificado'),
        ('report', 'Reporte / Informe'),
        ('manual', 'Manual / Procedimiento'),
        ('other', 'Otros Docs'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título del Documento")
    category = models.CharField(max_length=50, choices=CAT_CHOICES, default='other')
    file = models.FileField(upload_to='business_docs/', verbose_name="Archivo Digital")
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', verbose_name="Carpeta")
    
    # Vinculaciones opcionales para contexto
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    radiobase = models.ForeignKey(RadioBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    upload_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    
    # Control de versiones
    version_number = models.IntegerField(default=1, verbose_name="Versión Actual")
    
    # Tags para búsqueda
    tags = models.CharField(max_length=255, blank=True, null=True, verbose_name="Etiquetas")
    
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_category_display()}: {self.title} (v{self.version_number})"
    
    class Meta:
        verbose_name = "Documento Institucional"
        verbose_name_plural = "Documentos Institucionales"
        ordering = ['-upload_date']

class DocumentVersion(models.Model):
    """Historial de versiones de documentos"""
    document = models.ForeignKey(BusinessDocument, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField(verbose_name="Número de Versión")
    file = models.FileField(upload_to='business_docs/versions/', verbose_name="Archivo de esta Versión")
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Notas del Cambio")
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name="Tamaño (bytes)")
    
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"
    
    class Meta:
        verbose_name = "Versión de Documento"
        verbose_name_plural = "Versiones de Documentos"
        ordering = ['-version_number']
        unique_together = ['document', 'version_number']

class DocumentPermission(models.Model):
    """Control de permisos por documento o carpeta"""
    PERMISSION_CHOICES = [
        ('view', 'Solo Lectura'),
        ('edit', 'Edición'),
        ('full', 'Control Total'),
    ]
    
    # Puede ser documento o carpeta
    document = models.ForeignKey(BusinessDocument, on_delete=models.CASCADE, null=True, blank=True, related_name='permissions')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='permissions')
    
    # Permisos por usuario o rol
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='document_permissions')
    role = models.CharField(max_length=50, null=True, blank=True, verbose_name="Rol del Sistema")
    
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='view')
    
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_permissions')
    granted_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        target = self.document or self.folder
        subject = self.user or f"Rol: {self.role}"
        return f"{subject} - {self.get_permission_level_display()} en {target}"
    
    class Meta:
        verbose_name = "Permiso de Documento"
        verbose_name_plural = "Permisos de Documentos"
