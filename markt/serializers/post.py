from rest_framework import serializers
from ..models import Post, Empresa
from django.contrib.auth.models import User
from .user import UserSerializer
from .empresa import EmpresaSerializer

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email'] 
        
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre_fantasia'] 

class PostCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Post
        fields = '__all__'
        
class PostReadSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = '__all__'
        
    def get_author(self, obj):
        author_type = obj.author_type.model_class()

        if author_type == User:
            return UserSerializer(obj.author).data
        elif author_type == Empresa:
            return EmpresaSerializer(obj.author).data
        return None