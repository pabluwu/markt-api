from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import ContactoServicio
from ..serializers.contacto_servicio import ContactoServicioSerializer

class ContactoServicioViewSet(viewsets.ModelViewSet):
    queryset = ContactoServicio.objects.all()
    serializer_class = ContactoServicioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not serializer.is_valid():
            print(serializer.errors) 
        serializer.save(user=self.request.user)
        
            
