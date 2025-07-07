from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from ..models import RecursoUsuarios
from ..models import Empresa  # asegúrate de importar correctamente
from django.contrib.auth import get_user_model

User = get_user_model()

class RecursoUsuariosSerializer(serializers.ModelSerializer):
    author_type = serializers.CharField(write_only=True, required=False)
    author_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = RecursoUsuarios
        fields = '__all__'

    def validate(self, attrs):
        author_type = attrs.get('author_type', '').lower()
        author_id = attrs.get('author_id')

        if author_type == 'user':
            model = User
        elif author_type == 'empresa':
            model = Empresa
        else:
            raise serializers.ValidationError({'author_type': 'Debe ser "user" o "empresa"'})

        author = get_object_or_404(model, id=author_id)

        # Guardar para usar en create
        attrs['author_model'] = model
        attrs['author_instance'] = author
        return attrs

    def create(self, validated_data):
        model = validated_data.pop('author_model')
        author = validated_data.pop('author_instance')

        validated_data['author_type'] = ContentType.objects.get_for_model(model)
        validated_data['author_id'] = author.id

        return super().create(validated_data)

    def resolve_author(self, author_type, author_id):
        author_type = author_type.lower()
        if author_type == 'user':
            model = User
        elif author_type == 'empresa':
            model = Empresa
        else:
            raise serializers.ValidationError({'author_type': 'Debe ser "user" o "empresa"'})

        author = get_object_or_404(model, id=author_id)
        content_type = ContentType.objects.get_for_model(model)
        return content_type, author.id

    def update(self, instance, validated_data):
        author_type_str = validated_data.pop('author_type', None)
        author_id = validated_data.pop('author_id', None)

        if author_type_str and author_id:
            content_type, resolved_id = self.resolve_author(author_type_str, author_id)
            instance.author_type = content_type
            instance.author_id = resolved_id

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance