from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from ..serializers.empresa import EmpresaSerializer
from ..models import Empresa

class EmpresaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]  # Solo accesible con autenticación JWT
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer

    @action(detail=False, methods=['get'], url_path='getByUser')
    def get_by_user(self, request):
        """
        Obtiene las empresas asociadas al usuario autenticado
        """
        user = request.user  
        empresas = Empresa.objects.filter(usuarios=user)
        
        if empresas.exists():
            serializer = EmpresaSerializer(empresas, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "No se encontraron empresas asociadas a este usuario."}, status=404)

