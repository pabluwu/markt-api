from django.contrib.contenttypes.models import ContentType
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Seguimiento, Empresa
from django.contrib.auth import get_user_model

User = get_user_model()

class SeguimientoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = request.data
        user = request.user

        # Validar que el id_seguidor coincide con el usuario autenticado
        if int(data.get("id_seguidor")) != user.id:
            return Response({"error": "No tienes permiso para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)

        # Obtener ContentType del seguidor
        try:
            seguidor_content_type = ContentType.objects.get(model=data["type_seguidor"].lower())
        except ContentType.DoesNotExist:
            return Response({"error": "Tipo de seguidor inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener ContentType del seguido
        try:
            seguido_content_type = ContentType.objects.get(model=data["type_seguido"].lower())
        except ContentType.DoesNotExist:
            return Response({"error": "Tipo de seguido inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar seguimiento existente
        seguimiento, created = Seguimiento.objects.get_or_create(
            seguidor_content_type=seguidor_content_type,
            seguidor_object_id=data["id_seguidor"],
            seguido_content_type=seguido_content_type,
            seguido_object_id=data["id_seguido"]
        )

        # Si ya existía, eliminar (unfollow)
        if not created:
            seguimiento.delete()
            return Response({"message": "Se ha dejado de seguir con éxito."}, status=status.HTTP_200_OK)

        return Response({"message": "Seguimiento realizado con éxito."}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def check_follow(self, request):
        """
        Verifica si el usuario autenticado sigue a otro usuario o empresa.
        """
        user = request.user
        id_seguidor = request.query_params.get("id_seguidor")
        id_seguido = request.query_params.get("id_seguido")
        type_seguidor = request.query_params.get("type_seguidor")
        type_seguido = request.query_params.get("type_seguido")

        # Validar que el id_seguidor es el del usuario autenticado
        if not id_seguidor or int(id_seguidor) != user.id:
            return Response({"error": "No tienes permiso para verificar esta información."}, status=status.HTTP_403_FORBIDDEN)

        # Validar parámetros obligatorios
        if not (id_seguido and type_seguidor and type_seguido):
            return Response({"error": "Faltan parámetros requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener ContentType del seguidor
        try:
            seguidor_content_type = ContentType.objects.get(model=type_seguidor.lower())
        except ContentType.DoesNotExist:
            return Response({"error": "Tipo de seguidor inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener ContentType del seguido
        try:
            seguido_content_type = ContentType.objects.get(model=type_seguido.lower())
        except ContentType.DoesNotExist:
            return Response({"error": "Tipo de seguido inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el seguimiento existe
        existe = Seguimiento.objects.filter(
            seguidor_content_type=seguidor_content_type,
            seguidor_object_id=id_seguidor,
            seguido_content_type=seguido_content_type,
            seguido_object_id=id_seguido
        ).exists()

        return Response({"following": existe}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def seguidos(self, request):
        """
        Obtiene la lista de entidades que un usuario sigue.
        - Si se proporciona `id_seguidor`, obtiene los seguidos de ese usuario.
        - Si no se proporciona, usa el usuario autenticado.

        Query Params:
        - `id_seguidor` (opcional): ID del usuario del que se quieren ver los seguidos.

        Ejemplo de llamada:
        - `/api/seguimiento/seguidos/?id_seguidor=5`

        Respuesta:
        ```json
        [
            {
                "id": 2,
                "type": "empresa",
                "name": "Nombre de la Empresa"
            },
            {
                "id": 3,
                "type": "user",
                "name": "Nombre de Usuario"
            }
        ]
        ```
        """
        id_seguidor = request.query_params.get("id_seguidor")

        # Si no se proporciona id_seguidor, usamos el usuario autenticado
        if id_seguidor:
            try:
                usuario = User.objects.get(id=id_seguidor)
            except User.DoesNotExist:
                return Response({"error": "El usuario no existe."}, status=status.HTTP_404_NOT_FOUND)
        else:
            usuario = request.user  # Usuario autenticado

        # Obtener ContentType del usuario
        seguidor_content_type = ContentType.objects.get_for_model(usuario)

        # Buscar seguimientos donde el usuario sea el seguidor
        seguimientos = Seguimiento.objects.filter(
            seguidor_content_type=seguidor_content_type,
            seguidor_object_id=usuario.id
        )

        result = []
        for seg in seguimientos:
            seguido_obj = seg.seguido  # Obtener el objeto seguido
            print(seg.seguido)

            # Determinar el nombre y username (si existen)
            name = getattr(seguido_obj, "name", None) or getattr(seguido_obj, "nombre_fantasia", None) or str(seguido_obj)
            username = getattr(seguido_obj, "username", None)
            
            if isinstance(seguido_obj, User):  # Si es un usuario
                imagen_perfil = getattr(seguido_obj.userprofile, "imagen_perfil", None)
                if imagen_perfil:
                    imagen_perfil = imagen_perfil.url
                else: 
                    imagen_perfil = None
            elif isinstance(seguido_obj, Empresa):  # Si es una empresa
                imagen_perfil = getattr(seguido_obj, "imagen_perfil", None)
                if imagen_perfil:
                    imagen_perfil = imagen_perfil.url  # Devolver la URL de la imagen
            else:
                imagen_perfil = None  # Si no es ni un usuario ni una empresa, no tiene imagen

            result.append({
                "id": seg.seguido_object_id,
                "type": seg.seguido_content_type.model,
                "name": name,
                "username": username,  # Puede ser None si no existe
                "imagen_perfil": imagen_perfil,  # Agregar la imagen de perfil
            })

        return Response(result, status=status.HTTP_200_OK)