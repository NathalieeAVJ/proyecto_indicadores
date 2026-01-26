from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from inventory.models import PhoneNumber

class SimCard(models.Model):
    TYPE_CHOICES = [
        ('physical', 'SIM Física'),
        ('esim', 'eSIM (Virtual)'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('sold', 'Vendida'),
        ('defective', 'Defectuosa'),
        ('deactivated', 'Desactivada / Migrada'),
    ]
    
    iccid = models.CharField(max_length=20, unique=True, verbose_name="ICCID")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='physical', verbose_name="Tipo de SIM")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Estado")
    
    phone_number = models.OneToOneField(
        PhoneNumber, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sim_card',
        verbose_name="Número Asignado"
    )
    
    puk = models.CharField(max_length=20, verbose_name="PUK")
    pin = models.CharField(max_length=10, verbose_name="PIN")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_type_display()} - {self.iccid} ({self.get_status_display()})"

    class Meta:
        verbose_name = "SIM Card"
        verbose_name_plural = "SIM Cards"

class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre / Razón Social")
    dni = models.CharField(max_length=30, unique=True, verbose_name="Cédula / RIF / Pasaporte")
    email = models.EmailField(verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=20, verbose_name="Teléfono de Contacto")
    address = models.TextField(verbose_name="Dirección de Domicilio")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.dni})"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta (Punto de Venta)'),
        ('transfer', 'Transferencia / Pago Móvil'),
        ('zelle', 'Zelle'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='purchases', verbose_name="Cliente")
    sim_card = models.OneToOneField(SimCard, on_delete=models.PROTECT, related_name='sale', verbose_name="SIM Card Vendida")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de la Venta (USD)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Método de Pago")
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='sales_made',
        verbose_name="Vendedor"
    )
    
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Venta")
    notes = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    
    contract_pdf = models.FileField(upload_to='contracts/sales/', blank=True, null=True, verbose_name="Contrato Digital")
    
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Al realizar una venta, marcar la SIM como vendida
            self.sim_card.status = 'sold'
            self.sim_card.save()

    def __str__(self):
        return f"Venta {self.id} - {self.customer.name} ({self.sim_card.iccid})"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-sale_date']
