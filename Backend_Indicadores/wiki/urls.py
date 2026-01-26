from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TechArticleViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'articles', TechArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
