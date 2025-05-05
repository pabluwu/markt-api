from rest_framework import serializers
from ..models import ArchivoAdjunto

class ArchivoAdjuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivoAdjunto
        fields = ['id', 'servicio', 'archivo',]
