from rest_framework import serializers
from ..models import Empresa

class EmpresaSerializer(serializers.ModelSerializer):
    imagen_perfil = serializers.ImageField(required=False)
    class Meta:
        model = Empresa
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Solo dejar la ruta del archivo sin el dominio completo
        if instance.imagen_perfil:
            representation["imagen_perfil"] = 'media/'+instance.imagen_perfil.name  # Solo el path relativo

        return representation
