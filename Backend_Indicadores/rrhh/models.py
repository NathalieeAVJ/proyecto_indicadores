from django.db import models
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords
from decimal import Decimal

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Departamento")
    description = models.TextField(blank=True, verbose_name="Funciones Específicas")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_departments', verbose_name="Departamento Superior")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def get_descendants(self):
        """Retorna todos los departamentos que dependen de este, recursivamente."""
        descendants = []
        for child in self.sub_departments.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['name']

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('vacation', 'En Vacaciones'),
        ('on_leave', 'Permiso/Reposo'),
        ('retired', 'Retirado'),
        ('blacklisted', 'Lista Negra / Egresado'),
    ]
    CONTRACT_TYPES = [
        ('permanent', 'Fijo / Indeterminado'),
        ('temporary', 'Contratado / Determinado'),
        ('intern', 'Pasante'),
    ]

    HIERARCHY_LEVELS = [
        (0, 'Presidente'),
        (1, 'Vice Presidente'),
        (2, 'Gerente General'),
        (3, 'Gerente'),
        (4, 'Coordinador'),
        (5, 'Especialista / Operativo'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    system_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile', verbose_name="Usuario de Sistema")
    dni = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    
    position = models.CharField(max_length=100, verbose_name="Cargo")
    department = models.CharField(max_length=100, verbose_name="Departamento (Texto)", blank=True)
    department_ref = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees', verbose_name="Departamento")
    rank = models.IntegerField(choices=HIERARCHY_LEVELS, default=5, verbose_name="Nivel Jerárquico")
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', verbose_name="Supervisor Directo")
    
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, default='permanent', verbose_name="Tipo de Contrato")
    hire_date = models.DateField(verbose_name="Fecha de Ingreso")
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sueldo Base")
    
    hcm_policy_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nro Póliza HCM")
    emergency_contact = models.CharField(max_length=200, blank=True, null=True, verbose_name="Contacto de Emergencia")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Estado Laboral")
    
    blacklist_reason = models.TextField(blank=True, null=True, verbose_name="Motivo de Desincorporación")
    blacklist_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Egreso")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class FamilyMember(models.Model):
    RELATION_CHOICES = [
        ('spouse', 'Esposo/a'),
        ('child', 'Hijo/a'),
        ('parent', 'Padre/Madre'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='family')
    full_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATION_CHOICES)
    birth_date = models.DateField()
    dni = models.CharField(max_length=20, blank=True, null=True)
    history = HistoricalRecords()

class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('laptop', 'Computadora'),
        ('phone', 'Teléfono Celular'),
        ('tool', 'Herramienta'),
        ('uniform', 'Uniforme'),
        ('id_card', 'Carnet'),
        ('furniture', 'Mueble de Oficina'),
    ]
    STATUS_CHOICES = [
        ('functional', 'En Uso / Funcional'),
        ('failing', 'Presenta Fallas'),
        ('broken', 'Dañado / No Funciona'),
        ('maintenance', 'En Mantenimiento'),
        ('replaced', 'Sustituido / Retirado'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment', verbose_name="Asignado a")
    
    internal_code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Código de Activo/Inventario")
    item_name = models.CharField(max_length=100, verbose_name="Nombre del Equipo")
    brand = models.CharField(max_length=50, blank=True, null=True, verbose_name="Marca")
    model = models.CharField(max_length=50, blank=True, null=True, verbose_name="Modelo")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Categoría")
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Serie S/N")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='functional', verbose_name="Estado de Operatividad")
    assigned_date = models.DateField(auto_now_add=True, verbose_name="Fecha de Asignación")
    is_returned = models.BooleanField(default=False, verbose_name="Devuelto")
    
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.item_name} ({self.internal_code or 'S/C'})"

    class Meta:
        verbose_name = "Equipo / Activo"
        verbose_name_plural = "Equipos e Inventario"

class Absence(models.Model):
    TYPE_CHOICES = [
        ('vacation', 'Vacaciones'),
        ('medical', 'Reposo Médico'),
        ('personal', 'Permiso Personal'),
        ('bereavement', 'Duelo'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='absences')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reason = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()

class Payroll(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    period_month = models.IntegerField()
    period_year = models.IntegerField()
    
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    food_stamps = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Cesta Ticket")
    bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_date = models.DateField(null=True, blank=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Auto-assign default food stamps if zero
        if not self.food_stamps:
            self.food_stamps = Decimal('40.00')

        # Auto-calculate net salary
        self.net_salary = self.base_salary + self.food_stamps + self.bonuses - self.deductions
        super().save(*args, **kwargs)

class HRRequest(models.Model):
    REQUEST_TYPES = [
        ('vacation', 'Vacaciones'),
        ('benefits', 'Prestaciones Sociales'),
        ('certificate', 'Constancia de Trabajo'),
        ('loan', 'Préstamo/Adelanto'),
        ('equip_fault', 'Reporte de Falla de Equipo'),
        ('other', 'Otras Solicitudes'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='hr_requests', verbose_name="Solicitante")
    type = models.CharField(max_length=20, choices=REQUEST_TYPES, verbose_name="Tipo de Trámite")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    reason = models.TextField(verbose_name="Justificación / Detalle")
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='incident_requests', verbose_name="Equipo Involucrado")
    start_date = models.DateField(null=True, blank=True, verbose_name="Fecha Inicio (Si aplica)")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha Fin (Si aplica)")
    
    supervisor_comment = models.TextField(blank=True, verbose_name="Comentarios del Supervisor")
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_requests')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_type_display()} - {self.employee} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Solicitud de RRHH"
        verbose_name_plural = "Solicitudes de RRHH"
        ordering = ['-created_at']

class PerformanceEvaluation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluations', verbose_name="Empleado")
    period_month = models.IntegerField(verbose_name="Mes")
    period_year = models.IntegerField(verbose_name="Año")
    
    score = models.IntegerField(verbose_name="Calificación (1-100)")
    comments = models.TextField(blank=True, verbose_name="Comentarios de Desempeño")
    
    suggested_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Bono Sugerido ($)")
    bonus_approved = models.BooleanField(default=False, verbose_name="Bono Aprobado")
    
    evaluated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='evaluations_made')
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('employee', 'period_month', 'period_year')
        verbose_name = "Evaluación de Desempeño"
        verbose_name_plural = "Evaluaciones de Desempeño"
        ordering = ['-period_year', '-period_month']

    def __str__(self):
        return f"EVA - {self.employee} ({self.period_month}/{self.period_year})"

# Signals to sync Employee with System User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from incidencias.notifications import Notification

@receiver(post_save, sender=HRRequest)
def notify_hr_request_status(sender, instance, created, **kwargs):
    """Notifica al supervisor sobre nuevas solicitudes y al empleado sobre resoluciones."""
    if created:
        # Notificar al supervisor si existe y tiene usuario de sistema
        supervisor = instance.employee.supervisor
        if supervisor and supervisor.system_user:
            Notification.objects.create(
                user=supervisor.system_user,
                title="Nueva Solicitud de Autogestión",
                message=f"{instance.employee.first_name} ha solicitado {instance.get_type_display()}.",
                link="/approvals" # Ruta planeada para el frontend
            )
    else:
        # Notificar al empleado sobre el cambio de estado (Aprobado/Rechazado)
        if instance.status != 'pending' and instance.employee.system_user:
            verb = "aprobado" if instance.status == 'approved' else "rechazado"
            Notification.objects.create(
                user=instance.employee.system_user,
                title=f"Solicitud {verb.capitalize()}",
                message=f"Tu solicitud de {instance.get_type_display()} ha sido {verb}. Comentario: {instance.supervisor_comment}",
                link="/self-service"
            )

@receiver(post_save, sender=Employee)
def sync_employee_to_user(sender, instance, **kwargs):
    """Sincroniza los nombres y el correo del empleado con su usuario de acceso"""
    if instance.system_user:
        user = instance.system_user
        # Evitar recursión infinita si el usuario también salvara al empleado (no es el caso aquí)
        if (user.first_name != instance.first_name or 
            user.last_name != instance.last_name or 
            user.email != instance.email):
            user.first_name = instance.first_name
            user.last_name = instance.last_name
            user.email = instance.email
            user.save()

@receiver(post_delete, sender=Employee)
def delete_linked_user(sender, instance, **kwargs):
    """Elimina la cuenta de acceso cuando el empleado es retirado/borrado"""
    if instance.system_user:
        instance.system_user.delete()

class MaintenanceLog(models.Model):
    TYPE_CHOICES = [
        ('preventive', 'Preventivo / Rutina'),
        ('corrective', 'Correctivo / Reparación'),
        ('upgrade', 'Mejora / Upgrade'),
    ]
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_logs', verbose_name="Equipo")
    date = models.DateField(default=timezone.now, verbose_name="Fecha del Servicio")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='corrective', verbose_name="Tipo de Mantenimiento")
    description = models.TextField(verbose_name="Detalle del Trabajo")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo del Servicio ($)")
    performed_by = models.CharField(max_length=100, verbose_name="Técnico / Empresa Responsable")
    
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_type_display()} - {self.equipment} ({self.date})"

    class Meta:
        verbose_name = "Log de Mantenimiento"
        verbose_name_plural = "Logs de Mantenimientos"
        ordering = ['-date']
