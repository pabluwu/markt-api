from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from ..models import Comment
from ..serializers.comment import CommentSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        """Crea un comentario validando el tipo de commenter y el post"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """Permite filtrar por post_id si se envía como parámetro GET"""
        post_id = request.query_params.get('post_id')
        if post_id:
            comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
        else:
            comments = Comment.objects.all()
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)