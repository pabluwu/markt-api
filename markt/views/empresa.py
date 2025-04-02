from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from ..serializers.empresa import EmpresaSerializer
from ..models import Empresa

class EmpresaViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]  # Solo accesible con autenticación JWT
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    parser_classes = [MultiPartParser, FormParser]

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
        
    def update(self, request, *args, **kwargs):
        try:    
            """Maneja PUT y PATCH correctamente con FormData"""
            partial = kwargs.pop('partial', False)  # PATCH vs PUT
            instance = self.get_object()
            print(request.FILES)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                print('valido')
                serializer.save()
                return Response(serializer.data)
                return Response(serializer.errors, status=400)
            else:
                print(serializer.errors)
                print('mo valido')
        except Exception as e:
            print(e)
            return Response({"error": "No se pudo actualizar la empresa."}, status=400)
        return Response({"error": "No se pudo actualizar la empresa."}, status=400)

