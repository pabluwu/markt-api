from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from ..models import Perfil, Empresa
from ..serializers.perfil import PerfilSerializer
from django.shortcuts import get_object_or_404

class PerfilViewSet(viewsets.ModelViewSet):
    serializer_class = PerfilSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='switch-company')
    def switch_company(self, request):
        empresa_id = request.data.get('empresa_id')  # Obtener el ID de la empresa (puede ser None)
        user = request.user

        perfil, created = Perfil.objects.get_or_create(user=user)

        if empresa_id is None:
            # Si empresa_id es None, restablecer el perfil al estado de usuario (sin empresa)
            perfil.empresa = None
            perfil.save()
            return Response({"message": "Perfil cambiado a usuario", "empresa": None})

        # Si empresa_id no es None, asignar la empresa al perfil
        empresa = get_object_or_404(Empresa, id=empresa_id)
        perfil.empresa = empresa
        perfil.save()

        # Devuelve la empresa seleccionada en el perfil
        serializer = self.get_serializer(perfil)
        return Response(serializer.data)
