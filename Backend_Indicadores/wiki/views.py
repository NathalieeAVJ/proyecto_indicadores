from rest_framework import viewsets, permissions
from .models import Category, TechArticle
from .serializers import CategorySerializer, TechArticleSerializer
from users.models import AuditLog

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class TechArticleViewSet(viewsets.ModelViewSet):
    queryset = TechArticle.objects.all().select_related('category', 'author')
    serializer_class = TechArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category']

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            module='wiki_article',
            object_id=str(instance.id),
            description=f"Publicó un nuevo artículo técnico: {instance.title} en {instance.category.name}"
        )
