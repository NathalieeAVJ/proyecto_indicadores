from django.apps import AppConfig


class IncidenciasConfig(AppConfig):
    name = 'incidencias'

    def ready(self):
        import incidencias.signals
