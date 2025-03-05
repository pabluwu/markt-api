from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    rut = models.CharField(max_length=12, unique=True)  # Ejemplo: "12.345.678-9"
    nombre_empresa = models.CharField(max_length=50)
    nombre_fantasia = models.CharField(max_length=50)
    usuarios = models.ManyToManyField(User, related_name="empresas")  # Relación muchos a muchos con usuarios
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Se guarda automáticamente al crear
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_empresa

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)