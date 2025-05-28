from rest_framework import serializers
from ..models import Recurso

class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = '__all__'
        read_only_fields = ['autor']

    def create(self, validated_data):
        # El autor vendrá del request.user
        validated_data['autor'] = self.context['request'].user
        return super().create(validated_data)
