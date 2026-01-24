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
            module_name = request.path.split('/')[-2] if len(request.path.split('/')) > 2 else 'General'
            
            # Mask sensitive data if needed (e.g. passwords)
            description = f"Acción {request.method} en {request.path}. Status: {response.status_code}"
            
            AuditLog.objects.create(
                user=request.user,
                action=action_map.get(request.method, 'other'),
                module=module_name,
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
