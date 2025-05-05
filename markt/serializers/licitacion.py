from rest_framework import serializers
from ..models import Licitacion, Empresa, ArchivoLicitacion

class ArchivoLicitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivoLicitacion
        fields = ['id', 'archivo', 'licitacion']
class LicitacionSerializer(serializers.ModelSerializer):
    empresa = serializers.PrimaryKeyRelatedField(queryset=Empresa.objects.all())

    class Meta:
        model = Licitacion
        fields = ['id', 'titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'empresa']

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre_empresa', 'nombre_fantasia', 'rut', 'activa', 'imagen_perfil']
        
class LicitacionDetalleSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer()
    archivos = ArchivoLicitacionSerializer(many=True, source='archivos_licitacion')   

    class Meta:
        model = Licitacion
        fields = [
            'id',
            'titulo',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'empresa',
            'archivos'
        ]