from rest_framework import serializers
from .models import Folder, BusinessDocument, DocumentVersion, DocumentPermission

class FolderSerializer(serializers.ModelSerializer):
    subfolder_count = serializers.IntegerField(source='subfolders.count', read_only=True)
    document_count = serializers.IntegerField(source='documents.count', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Folder
        fields = '__all__'

class DocumentVersionSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = '__all__'

class DocumentPermissionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = DocumentPermission
        fields = '__all__'

class BusinessDocumentSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    folder_path = serializers.CharField(source='folder.get_full_path', read_only=True)
    
    # Campos anidados
    versions = DocumentVersionSerializer(many=True, read_only=True)
    permissions = DocumentPermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = BusinessDocument
        fields = '__all__'
