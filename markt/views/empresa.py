from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
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
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            print(request.FILES)

            # Convertir a un dict mutable
            data = request.data.copy()

            # Eliminar imagen_perfil si no viene archivo
            if 'imagen_perfil' not in request.FILES and 'imagen_perfil' in data:
                data.pop('imagen_perfil')

            serializer = self.get_serializer(instance, data=data, partial=partial)
            if serializer.is_valid():
                print('valido')
                serializer.save()
                return Response(serializer.data)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=400)
        except Exception as e:
            print(e)
            return Response({"error": "No se pudo actualizar la empresa."}, status=400)


    
    def create(self, request, *args, **kwargs):
        try:
            # Crear la empresa SIN el campo usuarios (porque no viene en request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            empresa = serializer.save()  # Guarda la empresa

            # Ahora agregamos el usuario autenticado al ManyToMany usuarios
            empresa.usuarios.add(request.user)
            empresa.save()

            # Respondemos con la empresa creada
            return Response(self.get_serializer(empresa).data, status=200)

        except Exception as e:
            print(e)
            return Response({"error": "No se pudo crear la empresa."}, status=status.HTTP_400_BAD_REQUEST)


