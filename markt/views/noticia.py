# noticias/views.py

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from ..models import Noticias
from ..serializers.noticia import NoticiaSerializer

class NoticiaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Noticias.objects.all().order_by('-fecha')
    serializer_class = NoticiaSerializer
    pagination_class = PageNumberPagination
