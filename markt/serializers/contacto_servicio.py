from rest_framework import serializers
from ..models import ContactoServicio

class ContactoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoServicio
        fields = "__all__"
        read_only_fields = ("user", "fecha")