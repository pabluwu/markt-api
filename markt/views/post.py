from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from django.contrib.contenttypes.models import ContentType
from ..models import Perfil, Empresa, Post
from django.contrib.auth.models import User
from ..serializers.post import PostCreateSerializer, PostReadSerializer
from django.shortcuts import get_object_or_404

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostReadSerializer
    queryset = Post.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Sobreescribe el método POST para asignar automáticamente el autor según el tipo de perfil activo."""
        
        data = request.data
        post_content = data.get("postContent")
        post_type = data.get("type")  # "user" o "empresa"
        author_id = data.get("author_id")

        # 🔹 Validación de datos obligatorios
        if not post_content or not post_type or not author_id:
            return Response({"error": "Faltan datos obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Buscar el modelo de autor según el tipo
        if post_type == "user":
            author_model = User
        elif post_type == "empresa":
            author_model = Empresa
        else:
            return Response({"error": "Tipo de perfil inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Verificar que el autor exista
        author = get_object_or_404(author_model, id=author_id)

        # 🔹 Crear el post
        post = Post.objects.create(
            content=post_content,
            author_type=ContentType.objects.get_for_model(author_model),
            author_id=author.id
        )

        # 🔹 Serializar y devolver la respuesta con los datos creados
        return Response(PostCreateSerializer(post).data, status=status.HTTP_201_CREATED)
        
        
    @action(detail=True, methods=['get'], url_path='empresa')
    def posts_by_empresa(self, request, pk=None):
        """Obtiene los posts de una empresa según su ID."""
        empresa = Empresa.objects.filter(id=pk).first()
        
        if not empresa:
            return Response({"error": "Empresa no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        posts = Post.objects.filter(author_type=ContentType.objects.get_for_model(Empresa), author_id=empresa.id).order_by('-created_at')
        serializer = PostReadSerializer(posts, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='user')
    def posts_by_user(self, request, pk=None):
        """Obtiene los posts de un usuario según su ID."""
        user = User.objects.filter(id=pk).first()
        
        if not user:
            return Response({"error": "User no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        posts = Post.objects.filter(author_type=ContentType.objects.get_for_model(User), author_id=user.id).order_by('-created_at')
        serializer = PostReadSerializer(posts, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)