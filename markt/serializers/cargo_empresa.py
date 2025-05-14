from rest_framework import serializers
from ..models import CargoEmpresa

class CargoEmpresaSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # o usa un UserSerializer reducido
    empresa = serializers.StringRelatedField()

    class Meta:
        model = CargoEmpresa
        fields = ['id', 'user', 'empresa', 'cargo', 'is_valido', 'fecha_postulacion', 'fecha_confirmacion']
