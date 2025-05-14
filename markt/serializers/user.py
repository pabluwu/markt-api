from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import UserProfile, Empresa, CargoEmpresa
class EmpresaMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre_fantasia']


class CargoEmpresa(serializers.ModelSerializer):
    empresa = EmpresaMiniSerializer()

    class Meta:
        model = CargoEmpresa
        fields = ['cargo', 'is_valido', 'empresa']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["fecha_nacimiento", "segundo_apellido", "rut", "direccion", "profesion", "sobre_mi", "imagen_perfil"]

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()
    cargo_empresa = CargoEmpresa(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'userprofile', 'cargo_empresa']


class UserIdEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']  # Solo incluye id y email
        