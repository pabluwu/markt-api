from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from ..serializers.user import UserSerializer, UserIdEmailSerializer
from ..models import UserProfile
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from datetime import datetime

class UsuarioViewSet(ViewSet):
    permission_classes = [IsAuthenticated]  # Solo accesible con autenticación JWT

    def list(self, request):
        """
        Devuelve los datos del usuario autenticado.
        """
        user = request.user  # Obtiene el usuario a partir del token JWT
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def id_email_all(self, request):
        """
        Devuelve una lista paginada de todos los usuarios con su id y email.
        """
        users = User.objects.all()
        serializer = UserIdEmailSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-username/(?P<username>[^/.]+)')
    def get_by_username(self, request, username=None):
        """
        Obtiene la información de un usuario por su username.
        """
        user = get_object_or_404(User, username=username)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='update-user')
    def update_user(self, request, pk=None):
        """
        Permite actualizar los datos del usuario autenticado y su perfil.
        La URL debe incluir el ID del usuario y debe coincidir con el usuario autenticado.
        """
        user = request.user

        # Verificar que el usuario autenticado solo pueda modificar su propia información
        if str(user.id) != str(pk):
            return Response({"error": "No tienes permiso para modificar este usuario."}, status=status.HTTP_403_FORBIDDEN)

        # Obtener perfil del usuario
        userprofile, _ = UserProfile.objects.get_or_create(user=user)

        # Actualizar campos de User
        user.first_name = request.data.get("nombre", user.first_name)
        user.last_name = request.data.get("primer_apellido", user.last_name)
        user.save()

        # Actualizar campos de UserProfile
        userprofile.rut = request.data.get("rut", userprofile.rut)
        userprofile.segundo_apellido = request.data.get("segundo_apellido", userprofile.segundo_apellido)
        userprofile.profesion = request.data.get("profesion", userprofile.profesion)
        userprofile.direccion = request.data.get("direccion", userprofile.direccion)
        userprofile.sobre_mi = request.data.get("sobre_mi", userprofile.sobre_mi)
        fecha_nacimiento = request.data.get("fecha_nacimiento")
        if fecha_nacimiento:
            try:
                # Convertir ISO 8601 a YYYY-MM-DD
                fecha_nacimiento = datetime.strptime(fecha_nacimiento[:10], "%Y-%m-%d").date()
                userprofile.fecha_nacimiento = fecha_nacimiento
            except ValueError:
                return Response({"error": "Formato de fecha inválido. Usa YYYY-MM-DD o ISO 8601."},
                                status=status.HTTP_400_BAD_REQUEST)
        userprofile.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)