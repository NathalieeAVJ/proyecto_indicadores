from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from decimal import Decimal

class Employee(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('vacation', 'En Vacaciones'),
        ('on_leave', 'Permiso/Reposo'),
        ('retired', 'Retirado'),
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
    dni = models.CharField(max_length=20, unique=True, verbose_name="Cédula/ID")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    
    position = models.CharField(max_length=100, verbose_name="Cargo")
    department = models.CharField(max_length=100, verbose_name="Departamento")
    rank = models.IntegerField(choices=HIERARCHY_LEVELS, default=5, verbose_name="Nivel Jerárquico")
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', verbose_name="Supervisor Directo")
    
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, default='permanent', verbose_name="Tipo de Contrato")
    hire_date = models.DateField(verbose_name="Fecha de Ingreso")
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sueldo Base")
    
    hcm_policy_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nro Póliza HCM")
    emergency_contact = models.CharField(max_length=200, blank=True, null=True, verbose_name="Contacto de Emergencia")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Estado Laboral")
    
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
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='equipment')
    item_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    assigned_date = models.DateField(auto_now_add=True)
    is_returned = models.BooleanField(default=False)
    history = HistoricalRecords()

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

# Signals to sync Employee with System User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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
