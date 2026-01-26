from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('operative', 'Operativo'),
        ('maintenance', 'En Taller'),
        ('broken', 'Fuera de Servicio'),
        ('leased', 'Alquilado / Tercero'),
    ]
    
    plate = models.CharField(max_length=20, unique=True, verbose_name="Placa")
    brand = models.CharField(max_length=50, verbose_name="Marca")
    model = models.CharField(max_length=50, verbose_name="Modelo")
    year = models.IntegerField(verbose_name="Año")
    color = models.CharField(max_length=30, blank=True, null=True)
    odometer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Kilometraje Actual")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operative')
    
    insurance_policy = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cód. Póliza")
    insurance_expiry = models.DateField(blank=True, null=True, verbose_name="Vencimiento Seguro")
    
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate})"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

class FuelLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_logs')
    date = models.DateField(default=timezone.now)
    liters = models.DecimalField(max_digits=10, decimal_places=2)
    cost_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Total ($)")
    odometer_reading = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Lectura Odómetro")
    
    station = models.CharField(max_length=100, blank=True, null=True, verbose_name="Estación de Servicio")
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.vehicle} - {self.date} - {self.liters}L"

    class Meta:
        verbose_name = "Registro de Combustible"
        verbose_name_plural = "Registros de Combustible"
        ordering = ['-date']

class VehicleMaintenance(models.Model):
    TYPE_CHOICES = [
        ('preventive', 'Preventivo (Aceite/Cauchos)'),
        ('corrective', 'Correctivo / Reparación'),
        ('inspection', 'Inspección Rutinaria'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenances')
    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='preventive')
    description = models.TextField(verbose_name="Descripción del Trabajo")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performed_by = models.CharField(max_length=100, verbose_name="Taller / Responsable")
    next_due_odometer = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Próximo a (Km)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_type_display()} - {self.vehicle} ({self.date})"

    class Meta:
        verbose_name = "Mantenimiento Vehicular"
        verbose_name_plural = "Mantenimientos Vehiculares"
        ordering = ['-date']
