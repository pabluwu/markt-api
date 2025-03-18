from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    segundo_apellido = models.CharField(max_length=255, blank=True, null=True)
    rut = models.CharField(max_length=9, unique=True, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    profesion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username
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

class Post(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    author_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    author_id = models.PositiveIntegerField()
    author = GenericForeignKey('author_type', 'author_id')

    def __str__(self):
        return f"Post by {self.author}"
    
class Seguimiento(models.Model):
    seguidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="siguiendo") #Usuario que sigue
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) #Tipo de obj al que va a seguir, empresa o usuario.
    object_id = models.PositiveIntegerField() 
    seguido = GenericForeignKey('content_type', 'object_id')
    fecha_seguimiento = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('seguidor', 'content_type', 'object_id')  # Un usuario no puede seguir dos veces lo mismo

    def __str__(self):
        return f"{self.seguidor} sigue a {self.seguido}"