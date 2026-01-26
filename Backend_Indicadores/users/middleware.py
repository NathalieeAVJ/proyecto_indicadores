import json
from .models import AuditLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log only authenticated mutations (Create, Update, Delete)
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Skip logging for the logs themselves and media/static
            if 'audit-logs' in request.path or '/media/' in request.path or '/static/' in request.path:
                return response

            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete'
            }

            # Generate description based on path and status
            path_parts = [p for p in request.path.split('/') if p]
            module_name = path_parts[-2] if len(path_parts) >= 2 else 'General'
            object_id = path_parts[-1] if len(path_parts) >= 2 and path_parts[-1].isdigit() else None
            
            # Mask sensitive data if needed (e.g. passwords)
            description = f"Acción {request.method} en el módulo {module_name}"
            if object_id:
                description += f" (ID: {object_id})"
            description += f". Respuesta: {response.status_code}"
            
            AuditLog.objects.create(
                user=request.user,
                action=action_map.get(request.method, 'other'),
                module=module_name,
                object_id=object_id,
                description=description,
                ip_address=self.get_client_ip(request)
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
