from rest_framework import serializers, viewsets, permissions
from .models import WorkOrder

class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = '__all__'

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtering: Techs see only their orders, Admins see all
        user = self.request.user
        if user.role == 'admin':
            return WorkOrder.objects.all()
        return WorkOrder.objects.filter(assigned_to=user)
