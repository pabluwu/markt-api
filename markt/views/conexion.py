from django.contrib.contenttypes.models import ContentType
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Conexion, Empresa
from django.contrib.auth import get_user_model

User = get_user_model()

class ConexionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        data = request.data
        user = request.user        

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
        seguimiento, created = Conexion.objects.get_or_create(
            seguidor_content_type=seguidor_content_type,
            seguidor_object_id=user.id,
            seguido_content_type=seguido_content_type,
            seguido_object_id=data["id_seguido"],
            detalle_conexion=data["detalle_conexion"]
        )

        return Response({"message": "Seguimiento realizado con éxito."}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def check_conexion(self, request):
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
        existe = Conexion.objects.filter(
            seguidor_content_type=seguidor_content_type,
            seguidor_object_id=id_seguidor,
            seguido_content_type=seguido_content_type,
            seguido_object_id=id_seguido
        ).exists()

        return Response({"following": existe}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def conectados(self, request):
        id_seguidor = request.query_params.get("id_conectado")

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
        seguimientos = Conexion.objects.filter(
            seguidor_content_type=seguidor_content_type,
            seguidor_object_id=usuario.id
        )
        print(seguimientos)
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
                "detalle_conexion": seg.detalle_conexion,
                "estado": seg.estado,
                "fecha_seguimiento":seg.fecha_seguimiento
                
            })

        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def solicitudes_conexion(self, request):
        id_search = request.query_params.get("id")
        type_search = request.query_params.get("type")
        estado = request.query_params.get("estado")
        
        # user = request.user  
        # empresas = Empresa.objects.filter(usuarios=user, id=id_search)
        seguidor_content_type = ContentType.objects.get(model=type_search.lower())
        solicitudes = Conexion.objects.filter(
            seguido_content_type=seguidor_content_type,
            seguido_object_id=id_search,
            estado = estado
        )
    
        result = []
        for seg in solicitudes:
            seguido_obj = seg.seguidor  # Obtener el objeto seguido

            name = getattr(seguido_obj, "name", None) or getattr(seguido_obj, "nombre_fantasia", None) or str(seguido_obj)
            username = getattr(seguido_obj, "username", None)
            
            if isinstance(seguido_obj, User): 
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
                "id": seg.id,
                "type": seg.seguidor_content_type.model,
                "name": name,
                "username": username,  # Puede ser None si no existe
                "imagen_perfil": imagen_perfil,  # Agregar la imagen de perfil
                "detalle_conexion": seg.detalle_conexion,
                "estado": seg.estado,
                "fecha_seguimiento":seg.fecha_seguimiento
            })

        return Response(result, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['put'], url_path='actualizar-estado')
    def actualizar_estado(self, request):
        """
        Actualiza el campo 'estado' de una conexión específica.
        Body esperado:
        {
            "id": 1,
            "estado": 1
        }
        """
        conexion_id = request.data.get("id")
        nuevo_estado = request.data.get("estado")
        print('entra a actualizar estadi')
        if conexion_id is None or nuevo_estado is None:
            return Response({"error": "Se requiere 'id' y 'estado'."}, status=status.HTTP_400_BAD_REQUEST)

        print(conexion_id, nuevo_estado)
        try:
            conexion = Conexion.objects.get(id=conexion_id)
        except Conexion.DoesNotExist:
            return Response({"error": "Conexión no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        conexion.estado = nuevo_estado
        conexion.save()

        return Response({"message": "Estado actualizado correctamente."}, status=status.HTTP_200_OK)

        