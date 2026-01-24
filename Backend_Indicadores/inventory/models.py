from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords

class PhoneNumber(models.Model):
    number = models.CharField(max_length=20, unique=True, verbose_name="Número Telefónico")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción / Alias")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ubicación Física")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number} - {self.description or 'Sin descripción'}"

    class Meta:
        verbose_name = "Número Telefónico"
        verbose_name_plural = "Números Telefónicos"

class RadioBase(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Radiobase")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código de Estación")
    location = models.CharField(max_length=200, verbose_name="Ubicación / Dirección")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Radiobase"
        verbose_name_plural = "Radiobases"


# ==================== INVENTARIO DE REPUESTOS ====================

class SparePartCategory(models.Model):
    """Categoría de repuestos para clasificación"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría de Repuesto"
        verbose_name_plural = "Categorías de Repuestos"
        ordering = ['name']


class SparePart(models.Model):
    """Repuesto disponible en inventario"""
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    name = models.CharField(max_length=200, verbose_name="Nombre del Repuesto")
    category = models.ForeignKey(
        SparePartCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='spare_parts',
        verbose_name="Categoría"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Precio Unitario (USD)"
    )
    quantity_in_stock = models.IntegerField(default=0, verbose_name="Cantidad en Stock")
    minimum_stock = models.IntegerField(default=5, verbose_name="Stock Mínimo")
    location = models.CharField(max_length=100, blank=True, verbose_name="Ubicación en Almacén")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_low_stock(self):
        """Indica si el stock está por debajo del mínimo"""
        return self.quantity_in_stock <= self.minimum_stock

    @property
    def total_value(self):
        """Valor total del inventario de este repuesto"""
        return self.quantity_in_stock * self.unit_price

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"
        ordering = ['name']


class SparePartUsage(models.Model):
    """Registro de uso de repuesto en una incidencia"""
    INCIDENT_TYPES = [
        ('phone', 'Teléfono'),
        ('radiobase', 'Radiobase'),
    ]
    
    spare_part = models.ForeignKey(
        SparePart, 
        on_delete=models.PROTECT,
        related_name='usages',
        verbose_name="Repuesto"
    )
    quantity_used = models.IntegerField(verbose_name="Cantidad Usada")
    unit_price_at_usage = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio Unitario al Momento del Uso"
    )
    incident_type = models.CharField(
        max_length=20, 
        choices=INCIDENT_TYPES,
        verbose_name="Tipo de Incidencia"
    )
    incident_id = models.IntegerField(verbose_name="ID de Incidencia")
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='spare_part_usages',
        verbose_name="Usado por"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Uso")

    def __str__(self):
        return f"{self.spare_part.name} x{self.quantity_used} - {self.get_incident_type_display()} #{self.incident_id}"

    @property
    def total_cost(self):
        """Costo total de este uso"""
        return self.quantity_used * self.unit_price_at_usage

    class Meta:
        verbose_name = "Uso de Repuesto"
        verbose_name_plural = "Usos de Repuestos"
        ordering = ['-used_at']


# ==================== PRESUPUESTOS ====================

class Budget(models.Model):
    """Presupuesto para compra de repuestos"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending', 'Pendiente de Aprobación'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('executed', 'Ejecutado'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción / Justificación")
    requested_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Monto Solicitado"
    )
    approved_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Monto Aprobado"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="Estado"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='requested_budgets',
        verbose_name="Solicitado por"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_budgets',
        verbose_name="Aprobado por"
    )
    approval_notes = models.TextField(blank=True, verbose_name="Notas de Aprobación")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"
    
    @property
    def calculated_total(self):
        """Calcula el total basado en los items del presupuesto"""
        return sum(item.subtotal for item in self.items.all())

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        ordering = ['-created_at']


class BudgetItem(models.Model):
    """Ítem de un presupuesto - repuesto solicitado"""
    budget = models.ForeignKey(
        Budget, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Presupuesto"
    )
    spare_part = models.ForeignKey(
        SparePart, 
        on_delete=models.PROTECT,
        related_name='budget_items',
        verbose_name="Repuesto"
    )
    quantity = models.IntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio Unitario"
    )

    def __str__(self):
        return f"{self.spare_part.name} x{self.quantity}"
    
    @property
    def subtotal(self):
        """Subtotal de este ítem"""
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = "Ítem de Presupuesto"
        verbose_name_plural = "Ítems de Presupuesto"
