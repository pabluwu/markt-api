from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from ..models import Comment, Post, Empresa

class CommentSerializer(serializers.ModelSerializer):
    commenter_type = serializers.CharField(write_only=True)  # Se usa en la creación, no en la respuesta
    commenter_id = serializers.IntegerField(write_only=True)
    post_id = serializers.IntegerField(write_only=True)  # Se usa en la creación
    commenter_name = serializers.SerializerMethodField()  # Se devuelve en la respuesta

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'content', 'commenter_type', 'commenter_id', 'commenter_name', 'created_at']
        read_only_fields = ['created_at', 'commenter_name']

    def create(self, validated_data):
        commenter_type = validated_data.pop('commenter_type')
        commenter_id = validated_data.pop('commenter_id')
        post_id = validated_data.pop('post_id')

        # Validamos si el post existe
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise serializers.ValidationError({"post_id": "El post no existe."})

        # Mapeo de tipo a ContentType
        if commenter_type == "user":
            content_type = ContentType.objects.get(model="user")
            if not User.objects.filter(id=commenter_id).exists():
                raise serializers.ValidationError({"commenter_id": "El usuario no existe."})
        elif commenter_type == "empresa":
            content_type = ContentType.objects.get(model="empresa")
            if not Empresa.objects.filter(id=commenter_id).exists():
                raise serializers.ValidationError({"commenter_id": "La empresa no existe."})
        else:
            raise serializers.ValidationError({"commenter_type": "Tipo de comentarista no válido."})

        # Crear el comentario
        comment = Comment.objects.create(
            post=post,
            commenter_type=content_type,
            commenter_id=commenter_id,
            content=validated_data["content"]
        )
        return comment

    def get_commenter_name(self, obj):
        """Devuelve el username si es un User o el nombre_fantasia si es una Empresa"""
        if obj.commenter_type.model == "user":
            user = User.objects.filter(id=obj.commenter_id).first()
            return user.username if user else "Usuario no encontrado"
        elif obj.commenter_type.model == "empresa":
            empresa = Empresa.objects.filter(id=obj.commenter_id).first()
            return empresa.nombre_fantasia if empresa else "Empresa no encontrada"
        return "Desconocido"
