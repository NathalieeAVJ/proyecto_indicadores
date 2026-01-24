from django.db import models
from django.conf import settings
from inventory.models import PhoneNumber, RadioBase
from simple_history.models import HistoricalRecords
from .notifications import Notification

class FailureType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tipo de Falla")
    description = models.TextField(blank=True, verbose_name="Descripción")

    def __str__(self):
        return self.name

class Incident(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_review', 'En Revisión'),
        ('solved', 'Solucionada'),
        ('postponed', 'Pospuesta'),
    ]

    title = models.CharField(max_length=200, verbose_name="Asunto")
    description = models.TextField(verbose_name="Detalle de la Incidencia")
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE, related_name='incidents', verbose_name="Número Afectado")
    failure_type = models.ForeignKey(FailureType, on_delete=models.SET_NULL, null=True, verbose_name="Tipo de Falla")
    
    # Fechas
    start_date = models.DateTimeField(verbose_name="Fecha de Inicio de Falla")
    review_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Revisión")
    solved_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Solucionada")
    
    # Usuarios
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_incidents', verbose_name="Creado por")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents', verbose_name="Asignado a")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    solution_comment = models.TextField(blank=True, verbose_name="Comentarios de Solución")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"
        ordering = ['-created_at']

class RadioBaseIncident(models.Model):
    STATUS_CHOICES = Incident.STATUS_CHOICES

    title = models.CharField(max_length=200, verbose_name="Asunto")
    description = models.TextField(verbose_name="Detalle de la Incidencia")
    radio_base = models.ForeignKey(RadioBase, on_delete=models.CASCADE, related_name='incidents', verbose_name="Radiobase Afectada")
    failure_type = models.ForeignKey(FailureType, on_delete=models.SET_NULL, null=True, verbose_name="Tipo de Falla")
    
    # Fechas
    start_date = models.DateTimeField(verbose_name="Fecha de Inicio de Falla")
    review_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Revisión")
    solved_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Solucionada")
    
    # Usuarios
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_rb_incidents', verbose_name="Creado por")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_rb_incidents', verbose_name="Asignado a")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    solution_comment = models.TextField(blank=True, verbose_name="Comentarios de Solución")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"RB-#{self.id} - {self.title} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = "Incidencia de Radiobase"
        verbose_name_plural = "Incidencias de Radiobases"
        ordering = ['-created_at']

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Asignada'),
        ('in_progress', 'En Proceso'),
        ('testing', 'En Pruebas'),
        ('completed', 'Completada'),
    ]

    incident_type = models.CharField(max_length=20, choices=[('phone', 'Teléfono'), ('radiobase', 'Radiobase')])
    incident_id = models.IntegerField() # Link to ID
    
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Checklist
    checked_power = models.BooleanField(default=False)
    checked_wiring = models.BooleanField(default=False)
    checked_config = models.BooleanField(default=False)
    
    # Evidence
    photo_before = models.ImageField(upload_to='work_orders/', null=True, blank=True)
    photo_after = models.ImageField(upload_to='work_orders/', null=True, blank=True)
    
    technician_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"OT-{self.id} for {self.incident_type} #{self.incident_id}"

    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
