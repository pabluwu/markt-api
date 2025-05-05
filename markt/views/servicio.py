from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import Servicio, ProductoServicio
from ..serializers.servicio import ServicioSerializer, ServicioDetalleSerializer
from ..serializers.contacto_servicio import ContactoServicioSerializer
from ..serializers.archivo_servicio import ArchivoAdjuntoSerializer

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioDetalleSerializer
    
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
            
    @action(detail=False, methods=['get'], url_path='detalle-servicio')
    def detalle_servicio(self, request):
        servicio_id = request.query_params.get('servicio_id', None)
        
        if not servicio_id:
            return Response({"error": "Debe proporcionar el parámetro 'servicio_id'"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            servicio = Servicio.objects.get(id=servicio_id)
        except Servicio.DoesNotExist:
            return Response({"error": "Servicio no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ServicioDetalleSerializer(servicio,context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def contactos(self, request, pk=None):
        print('test')
        servicio = self.get_object()  # obtiene el Servicio específico

        contactos = servicio.contactos.all()  # gracias al related_name

        serializer = ContactoServicioSerializer(contactos, many=True)

        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def agregar_archivo(self, request, pk=None):
        try:
            servicio = self.get_object()
            print('\n servicio', request.data)
            serializer = ArchivoAdjuntoSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                print(e)
            if serializer.is_valid():
                archivo = serializer.save(servicio=servicio)
                return Response(ArchivoAdjuntoSerializer(archivo).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('\n',e)
            
        
