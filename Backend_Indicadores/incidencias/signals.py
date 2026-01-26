from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Incident, RadioBaseIncident, Notification

@receiver(post_save, sender=Incident)
def notify_incident_assignment(sender, instance, created, **kwargs):
    if instance.assigned_to:
        Notification.objects.get_or_create(
            user=instance.assigned_to,
            title="Nueva Incidencia Asignada",
            message=f"Se te ha asignado la incidencia: {instance.title}",
            link=f"/incidents/{instance.id}"
        )

@receiver(post_save, sender=RadioBaseIncident)
def notify_rb_incident_assignment(sender, instance, created, **kwargs):
    if instance.assigned_to:
        Notification.objects.get_or_create(
            user=instance.assigned_to,
            title="Nueva Falla de Radiobase",
            message=f"Se te ha asignado la falla: {instance.title}",
            link=f"/rb-incidents/{instance.id}"
        )
