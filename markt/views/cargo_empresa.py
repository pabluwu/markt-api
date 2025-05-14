# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from ..models import CargoEmpresa, Empresa
from django.utils import timezone
from ..serializers.cargo_empresa import CargoEmpresaSerializer

class CargoEmpresaViewSet(viewsets.ViewSet):
    """
    Lista todos los cargos de una empresa, con filtro opcional por is_valido.
    """

    def list(self, request):
        empresa_id = request.query_params.get('empresa_id')
        is_valido = request.query_params.get('is_valido')

        if not empresa_id:
            return Response({"error": "Debe proporcionar 'empresa_id' en los parámetros."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            empresa = Empresa.objects.get(pk=empresa_id)
        except Empresa.DoesNotExist:
            return Response({"error": "Empresa no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        queryset = CargoEmpresa.objects.filter(empresa=empresa)

        if is_valido in ['0', '1']:
            queryset = queryset.filter(is_valido=bool(int(is_valido)))

        # print('antes serializer')
        serializer = CargoEmpresaSerializer(queryset, many=True)
        # print('depsues serializer',serializer)
        return Response(serializer.data)


    @action(detail=True, methods=['put'], url_path='actualizar-validacion')
    def actualizar_validacion(self, request, pk=None):
        """
        Actualiza el estado de validación (is_valido) de un cargo específico.
        Recibe en el body: {"is_valido": true} o {"is_valido": false}
        """
        try:
            try:
                cargo = CargoEmpresa.objects.get(pk=pk)
            except CargoEmpresa.DoesNotExist:
                return Response({"error": "Cargo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

            is_valido = request.data.get("is_valido")
            if is_valido is None:
                return Response({"error": "'is_valido' es requerido en el cuerpo de la solicitud."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Convertir a booleano
            if isinstance(is_valido, bool):
                cargo.is_valido = is_valido
            elif str(is_valido).lower() in ['true', '1']:
                cargo.is_valido = True
            elif str(is_valido).lower() in ['false', '0']:
                cargo.is_valido = False
            else:
                return Response({"error": "Valor inválido para 'is_valido'. Debe ser true/false o 1/0."},
                                status=status.HTTP_400_BAD_REQUEST)

            if cargo.is_valido:
                cargo.fecha_confirmacion = timezone.now()
            else:
                cargo.fecha_confirmacion = None

            cargo.save()
            return Response(CargoEmpresaSerializer(cargo).data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Ocurrió un error al actualizar el cargo: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
