from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import UserProfile
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["fecha_nacimiento", "segundo_apellido", "rut", "direccion", "profesion"]

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'userprofile']


class UserIdEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']  # Solo incluye id y email
        