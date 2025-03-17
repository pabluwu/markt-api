from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from ..serializers.user import UserSerializer, UserIdEmailSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

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