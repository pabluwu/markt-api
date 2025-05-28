from rest_framework import viewsets, permissions, parsers
from ..models import Recurso
from ..serializers.recurso import RecursoSerializer
from ..permissions import IsAuthenticatedOrReadOnlyCustom

class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recurso.objects.all()
    serializer_class = RecursoSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyCustom]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)
