from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import OfertaLicitacion, Licitacion, Servicio
from ..serializers.servicio import ServicioSerializer
from ..serializers.servicio_licitacion import OfertaLicitacionSerializer

class ServicioLicitacionViewSet(viewsets.ModelViewSet):
    
    queryset = Servicio.objects.all()
    serializer_class = OfertaLicitacionSerializer

    def get_queryset(self):
        queryset = OfertaLicitacion.objects.all()
        licitacion_id = self.request.query_params.get('licitacion_id')
        if licitacion_id is not None:
            queryset = queryset.filter(licitacion_id=licitacion_id)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            print(request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            servicio = serializer.save()

            # Después de crear el servicio, creamos la OfertaLicitacion
            licitacion_id = request.data.get('licitacion_id')
            if not licitacion_id:
                return Response({"error": "El campo 'licitacion_id' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                licitacion = Licitacion.objects.get(id=licitacion_id)
            except Licitacion.DoesNotExist:
                return Response({"error": "Licitación no encontrada."}, status=status.HTTP_404_NOT_FOUND)

            OfertaLicitacion.objects.create(
                licitacion=licitacion,
                empresa_ofertante=servicio.empresa,
                servicio_ofertado=servicio,
                mensaje="Oferta creada automáticamente desde Servicio"
            )

            return Response({
                "message": "Servicio y oferta creados exitosamente.",
                "servicio": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
