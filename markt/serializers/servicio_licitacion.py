from rest_framework import serializers
from ..models import OfertaLicitacion
from ..serializers.servicio import ServicioDetalleSerializer
class OfertaLicitacionSerializer(serializers.ModelSerializer):
    servicio_ofertado = ServicioDetalleSerializer(read_only=True)

    class Meta:
        model = OfertaLicitacion
        fields = ['id', 'licitacion', 'empresa_ofertante', 'servicio_ofertado', 'fecha_oferta', 'mensaje']
