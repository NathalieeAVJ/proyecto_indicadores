from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()

class Supplier(models.Model):
    """Proveedor o Contratista"""
    CATEGORY_CHOICES = [
        ('materials', 'Materiales y Equipos'),
        ('services', 'Servicios Técnicos'),
        ('construction', 'Construcción'),
        ('maintenance', 'Mantenimiento'),
        ('consulting', 'Consultoría'),
        ('transport', 'Transporte y Logística'),
        ('other', 'Otros'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('blocked', 'Bloqueado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre o Razón Social")
    rif = models.CharField(max_length=50, unique=True, verbose_name="RIF/NIT")
    email = models.EmailField(verbose_name="Email de Contacto")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    address = models.TextField(verbose_name="Dirección")
    website = models.URLField(blank=True, null=True, verbose_name="Sitio Web")
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Calificación Promedio")
    evaluation_count = models.IntegerField(default=0, verbose_name="Número de Evaluaciones")
    
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Internas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_suppliers')
    
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.name} ({self.rif})"
    
    def update_rating(self):
        """Actualiza la calificación promedio basada en las evaluaciones"""
        evaluations = self.evaluations.all()
        if evaluations:
            avg = sum([e.overall_score for e in evaluations]) / len(evaluations)
            self.rating = round(avg, 2)
            self.evaluation_count = len(evaluations)
            self.save()
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['name']

class SupplierContact(models.Model):
    """Contactos de un proveedor"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100, verbose_name="Nombre Completo")
    position = models.CharField(max_length=100, verbose_name="Cargo")
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False, verbose_name="Contacto Principal")
    
    def __str__(self):
        return f"{self.name} - {self.supplier.name}"
    
    class Meta:
        verbose_name = "Contacto de Proveedor"
        verbose_name_plural = "Contactos de Proveedores"

class Contract(models.Model):
    """Contrato con un proveedor"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('active', 'Vigente'),
        ('expired', 'Vencido'),
        ('cancelled', 'Cancelado'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Contrato")
    title = models.CharField(max_length=200, verbose_name="Título del Contrato")
    description = models.TextField(verbose_name="Descripción")
    
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Finalización")
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto del Contrato")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    attachment = models.FileField(upload_to='contracts/', blank=True, null=True, verbose_name="PDF del Contrato")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.contract_number} - {self.supplier.name}"
    
    @property
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'active'
    
    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-start_date']

class PurchaseOrder(models.Model):
    """Orden de Compra"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('received', 'Recibida'),
        ('cancelled', 'Cancelada'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Orden")
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')
    
    description = models.TextField(verbose_name="Descripción de la Orden")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Total")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_orders')
    requested_date = models.DateField(default=timezone.now, verbose_name="Fecha de Solicitud")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Entrega Esperada")
    
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        return f"OC-{self.order_number} - {self.supplier.name}"
    
    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-requested_date']

class SupplierEvaluation(models.Model):
    """Evaluación de desempeño de un proveedor"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='evaluations')
    contract = models.ForeignKey(Contract, on_delete=models.SET_NULL, null=True, blank=True)
    
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    evaluation_date = models.DateField(default=timezone.now)
    
    # Criterios de evaluación (1-5)
    quality_score = models.IntegerField(verbose_name="Calidad de Productos/Servicios")
    delivery_score = models.IntegerField(verbose_name="Cumplimiento de Plazos")
    service_score = models.IntegerField(verbose_name="Atención y Servicio")
    price_score = models.IntegerField(verbose_name="Relación Calidad-Precio")
    compliance_score = models.IntegerField(verbose_name="Cumplimiento de Normas")
    
    overall_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="Calificación General")
    
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()
    
    def save(self, *args, **kwargs):
        # Calcular calificación general
        self.overall_score = (
            self.quality_score + 
            self.delivery_score + 
            self.service_score + 
            self.price_score + 
            self.compliance_score
        ) / 5.0
        super().save(*args, **kwargs)
        
        # Actualizar calificación del proveedor
        self.supplier.update_rating()
    
    def __str__(self):
        return f"Evaluación {self.supplier.name} - {self.evaluation_date}"
    
    class Meta:
        verbose_name = "Evaluación de Proveedor"
        verbose_name_plural = "Evaluaciones de Proveedores"
        ordering = ['-evaluation_date']
