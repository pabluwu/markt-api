from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import Licitacion
from ..serializers.licitacion import LicitacionSerializer, LicitacionDetalleSerializer, ArchivoLicitacionSerializer

class LicitacionViewSet(viewsets.ModelViewSet):
    queryset = Licitacion.objects.all()
    serializer_class = LicitacionDetalleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Obtener el parámetro 'empresa_id' de los query params
        empresa_id = self.request.query_params.get('empresa_id', None)
        
        if empresa_id is not None:
            # Filtramos los servicios por la empresa
            queryset = queryset.filter(empresa_id=empresa_id)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='detalle-licitacion')
    def detalle_licitacion(self, request):
        licitacion_id = request.query_params.get('licitacion_id', None)
        
        if not licitacion_id:
            return Response({"error": "Debe proporcionar el parámetro 'licitacion_id'"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            servicio = Licitacion.objects.get(id=licitacion_id)
        except Licitacion.DoesNotExist:
            return Response({"error": "Servicio no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LicitacionDetalleSerializer(servicio)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def agregar_archivo(self, request, pk=None):
        try:
            licitacion = self.get_object()
            print('\n servicio', request.data)
            serializer = ArchivoLicitacionSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                print(e)
                return Response({"error": "No se pudo crear la empresa."}, status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                archivo = serializer.save(licitacion=licitacion)
                return Response(ArchivoLicitacionSerializer(archivo).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('\n',e)
            return Response({"error": "No se pudo crear la empresa."}, status=status.HTTP_400_BAD_REQUEST)
