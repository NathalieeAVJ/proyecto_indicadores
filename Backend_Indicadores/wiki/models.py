from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    icon = models.CharField(max_length=50, default='mdi-folder', verbose_name="Icono (MDI)")
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría Técnica"
        verbose_name_plural = "Categorías Técnicas"

class TechArticle(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles', verbose_name="Categoría")
    title = models.CharField(max_length=200, verbose_name="Título del Artículo")
    summary = models.CharField(max_length=500, blank=True, null=True, verbose_name="Resumen Breve")
    content = models.TextField(verbose_name="Contenido (Markdown/HTML)")
    
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Autor")
    
    # Archivos adjuntos (en un futuro se podría usar un modelo separado para múltiples archivos)
    attachment = models.FileField(upload_to='wiki_attachments/', blank=True, null=True, verbose_name="Archivo Adjunto (PDF/Diagrama)")
    
    tags = models.CharField(max_length=255, blank=True, null=True, verbose_name="Etiquetas / Tags")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Artículo Técnico"
        verbose_name_plural = "Artículos Técnicos"
        ordering = ['-updated_at']
