from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from ..models import Servicio, ProductoServicio
from ..serializers.servicio import ServicioSerializer

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Obtener el parámetro 'empresa_id' de los query params
        empresa_id = self.request.query_params.get('empresa_id', None)
        
        if empresa_id is not None:
            # Filtramos los servicios por la empresa
            queryset = queryset.filter(empresa_id=empresa_id)
        
        return queryset

    def create(self, request, *args, **kwargs):
        # Serializa los datos de entrada
        print(request.data)
        try:
            serializer = self.get_serializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                print(e)
            if serializer.is_valid():
                # Si los datos son válidos, guarda el servicio y los productos
                servicio = serializer.save()
                
                # Devuelve una respuesta con el servicio creado
                return Response({
                    "message": "Servicio creado exitosamente",
                    "servicio": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            # Si la validación falla, responde con los errores
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
        
