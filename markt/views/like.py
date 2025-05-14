from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from ..models import Post, Like, Empresa
from django.contrib.auth.models import User

class LikeViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def toggle_like(self, request):
        """
        Permite a un usuario o empresa dar like o quitar su like a un post.
        """
        post_id = request.data.get('post_id')
        liker_id = request.data.get('liker_id')
        like_type = request.data.get('like_type')
        print(like_type)
        print(liker_id)
        # Verificar que los datos necesarios estén presentes
        if not post_id or not liker_id or not like_type:
            return Response({"error": "post_id, liker_id y like_type son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el post
        post = get_object_or_404(Post, pk=post_id)

        # Determinar si el like_type es 'user' o 'empresa'
        if like_type == 'user':
            liker = get_object_or_404(User, pk=liker_id)
        elif like_type == 'empresa':
            liker = get_object_or_404(Empresa, pk=liker_id)
        else:
            return Response({"error": "El like_type debe ser 'user' o 'empresa'."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el ContentType correspondiente a la entidad (Usuario o Empresa)
        content_type = ContentType.objects.get_for_model(liker)

        # Verificar si ya existe un like para este post por este liker
        like = Like.objects.filter(post=post, liker_type=content_type, liker_id=liker.id)

        if like.exists():
            # Si ya existe, lo eliminamos
            print('vamos a quitar el like')
            like.delete()
            return Response({"message": "Like eliminado correctamente."}, status=status.HTTP_201_CREATED)
        else:
            # Si no existe, lo creamos
            print('vamos a crear el like')
            Like.objects.create(post=post, liker_type=content_type, liker_id=liker.id)
            return Response({"message": "Like agregado correctamente."}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def check_like(self, request):
        """
        Verifica si el usuario o empresa ha dado like a un post.
        """
        post_id = request.query_params.get('post_id')
        liker_id = request.query_params.get('liker_id')
        like_type = request.query_params.get('like_type')

        if not post_id or not liker_id or not like_type:
            return Response({"error": "post_id, liker_id y like_type son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        post = get_object_or_404(Post, pk=post_id)

        if like_type == 'user':
            liker = get_object_or_404(User, pk=liker_id)
        elif like_type == 'empresa':
            liker = get_object_or_404(Empresa, pk=liker_id)
        else:
            return Response({"error": "El like_type debe ser 'user' o 'empresa'."}, status=status.HTTP_400_BAD_REQUEST)

        content_type = ContentType.objects.get_for_model(liker)

        # Verificar si ya existe un like
        like_exists = Like.objects.filter(post=post, liker_type=content_type, liker_id=liker.id).exists()

        # print(like_type)
        # print(liker_id)
        if like_exists:
            # print('return exists')
            return Response({"liked": 1}, status=status.HTTP_200_OK)
        else:
            # print('return not exists')
            return Response({"liked": 0}, status=status.HTTP_200_OK)