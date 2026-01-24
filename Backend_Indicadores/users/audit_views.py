from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'full_name', 'action', 'module', 'description', 'ip_address', 'created_at']

    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return "Sistema"

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().select_related('user')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # STRICT ROLE CHECK: Only 'admin' role can see logs
        if self.request.user.role != 'admin':
            return AuditLog.objects.none()
        return super().get_queryset()

    @action(detail=False, methods=['post'])
    def create_manual(self, request):
        action = request.data.get('action', 'other')
        module = request.data.get('module', 'General')
        description = request.data.get('description', '')
        
        # Get Client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        AuditLog.objects.create(
            user=request.user,
            action=action,
            module=module,
            description=description,
            ip_address=ip
        )
        return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)
