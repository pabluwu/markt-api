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
    sobre_mi = models.CharField(max_length=255, blank=True, null=True)
    imagen_perfil = models.ImageField(upload_to='perfil_imagenes/', null=True, blank=True)

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
    # Seguidor genérico (puede ser un usuario, empresa, etc.)
    seguidor_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="seguimientos_realizados", default=1)
    seguidor_object_id = models.PositiveIntegerField(default=1)
    seguidor = GenericForeignKey('seguidor_content_type', 'seguidor_object_id')

    # Seguido genérico (puede ser un usuario, empresa, etc.)
    seguido_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="seguidores", default=1)
    seguido_object_id = models.PositiveIntegerField(default=1)
    seguido = GenericForeignKey('seguido_content_type', 'seguido_object_id')

    fecha_seguimiento = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor_content_type', 'seguidor_object_id', 'seguido_content_type', 'seguido_object_id')

    def __str__(self):
        return f"{self.seguidor} sigue a {self.seguido}"
    
class Like(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")  # Post al que se da like

    liker_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Puede ser Usuario o Empresa
    liker_id = models.PositiveIntegerField()  # ID del Usuario o Empresa
    liker = GenericForeignKey("liker_type", "liker_id")  # Enlace genérico

    created_at = models.DateTimeField(auto_now_add=True)  # Fecha del like

    class Meta:
        unique_together = ("post", "liker_type", "liker_id")  # Un usuario/empresa no puede dar like dos veces

    def __str__(self):
        return f"{self.liker} dio like a {self.post}"
    
class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")  # Post en el que se comenta
    content = models.TextField()  # Contenido del comentario

    commenter_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Puede ser Usuario o Empresa
    commenter_id = models.PositiveIntegerField()  # ID del Usuario o Empresa
    commenter = GenericForeignKey("commenter_type", "commenter_id")  # Enlace genérico

    created_at = models.DateTimeField(auto_now_add=True)  # Fecha del comentario

    def __str__(self):
        return f"{self.commenter} comentó en {self.post}"
    
    
class Region(models.Model):
    numero = models.IntegerField(blank=True)
    nombre = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre
    
class Servicio(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="servicios")
    descripcion = models.TextField()

    # Relación con regiones (zona de cobertura)
    regiones = models.ManyToManyField(Region, related_name="servicios")

    # Tiempo promedio de entrega
    tiempo_entrega = models.CharField(max_length=255, blank=True, null=True)

    # Modalidades de atención (Múltiples opciones)
    PRESENCIAL = "presencial"
    REMOTO = "remoto"
    TERRENO = "terreno"
    MODALIDADES_CHOICES = [
        (PRESENCIAL, "Presencial"),
        (REMOTO, "Remoto / Online"),
        (TERRENO, "En terreno / Despacho incluido"),
    ]
    modalidades_atencion = models.ManyToManyField("ModalidadAtencion", related_name="servicios")

    # Formas de pago aceptadas (Múltiples opciones)
    TRANSFERENCIA = "transferencia"
    CREDITO = "credito"
    WEBPAY = "webpay"
    CRIPTO = "cripto"
    FORMAS_PAGO_CHOICES = [
        (TRANSFERENCIA, "Transferencia"),
        (CREDITO, "Crédito 30-60-90 días"),
        (WEBPAY, "Webpay"),
        (CRIPTO, "Criptomonedas u otras"),
    ]
    formas_pago = models.ManyToManyField("FormaPago", related_name="servicios")

    # Certificaciones y garantías (Opcional)
    certificaciones = models.TextField(blank=True, null=True)

    # Archivos adjuntos (Opcional)
    archivos = models.ManyToManyField("ArchivoAdjunto", blank=True, related_name="servicios")

    # Datos de contacto
    contacto_nombre = models.CharField(max_length=255)
    contacto_cargo = models.CharField(max_length=255, blank=True, null=True)
    contacto_email = models.EmailField()
    contacto_telefono = models.CharField(max_length=20)
    contacto_web = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Servicio de {self.empresa.nombre_fantasia}"


class ProductoServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=255)
    descripcion_breve = models.TextField()
    unidad_venta = models.CharField(max_length=100)  # Ej: unidad, hora, proyecto
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    disponibilidad_geografica = models.ManyToManyField(Region, related_name="productos")

    def __str__(self):
        return self.nombre


class ModalidadAtencion(models.Model):
    nombre = models.CharField(max_length=255, choices=Servicio.MODALIDADES_CHOICES, unique=True)
    slug = models.CharField(max_length=255, blank=True, null='nullo')

    def __str__(self):
        return self.nombre


class FormaPago(models.Model):
    nombre = models.CharField(max_length=255, choices=Servicio.FORMAS_PAGO_CHOICES, unique=True)
    slug = models.CharField(max_length=255, blank=True, null='nullo')

    def __str__(self):
        return self.nombre


class ArchivoAdjunto(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="archivos_adjuntos")
    archivo = models.FileField(upload_to="archivos_adjuntos/")
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.archivo.name
