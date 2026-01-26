from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMINIPSTRATOR = 'admin'
    EVALUATOR = 'evaluator'
    SUPPORT = 'support'
    TECHNICIAN = 'technician'
    
    ROLE_CHOICES = [
        (ADMINIPSTRATOR, 'Administrador de Sistema'),
        (EVALUATOR, 'Evaluador'),
        (SUPPORT, 'Soporte al Cliente'),
        (TECHNICIAN, 'Técnico'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SUPPORT)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Creación'),
        ('update', 'Actualización'),
        ('delete', 'Eliminación'),
        ('login', 'Inicio de Sesión'),
        ('other', 'Otro'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuario")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    module = models.CharField(max_length=100, verbose_name="Módulo/Tabla")
    object_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ID Objeto")
    description = models.TextField(verbose_name="Descripción de la Acción")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"

    def __str__(self):
        return f"{self.user} - {self.action} - {self.module} ({self.created_at})"
