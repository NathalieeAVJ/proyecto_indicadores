from rest_framework import serializers
from .models import Category, TechArticle

class CategorySerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(source='articles.count', read_only=True)
    class Meta:
        model = Category
        fields = '__all__'

class TechArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = TechArticle
        fields = '__all__'
