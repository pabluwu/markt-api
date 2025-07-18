from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

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
    rut = models.CharField(max_length=30, unique=True)  # Ejemplo: "12.345.678-9"
    nombre_empresa = models.CharField(max_length=1000, null=True) 
    # giro = models.CharField(max_length=255)
    # rubro = models.CharField(max_length=255)
    nombre_fantasia = models.CharField(max_length=1000, null=True)
    usuarios = models.ManyToManyField(User, related_name="empresas")  # Relación muchos a muchos con usuarios
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now,)  # Se guarda automáticamente al crear
    fecha_creacion_empresa = models.DateTimeField(null=True, blank=True)  # Se guarda automáticamente al crear
    activa = models.BooleanField(default=True)
    imagen_perfil = models.ImageField(upload_to='perfil_imagenes/', null=True, blank=True)
    razon_social = models.CharField(max_length=1000, default='', null=True)
    sector = models.CharField(max_length=1000, default='', null=True)
    rubro = models.CharField(max_length=1000, default='', null=True)
    giro = models.CharField(max_length=1000, default='', null=True)
    telefono_empresa = models.BigIntegerField(default=1, null=True)
    email_empresa = models.EmailField(default='', blank=True, null=True)
    direccion_fisica = models.CharField(max_length=50, default='', null=True)
    pais = models.CharField(max_length=1000, default='', null=True)
    region = models.CharField(max_length=1000, default='', null=True)
    comuna = models.CharField(max_length=1000, default='', null=True)
    pagina_web = models.CharField(max_length=1000, default='', null=True)
    nombre_representante_legal = models.CharField(max_length=1000, default='', null=True)
    correo_representante_legal = models.EmailField(max_length=1000, default='', null=True)
    telefono_representante_legal = models.BigIntegerField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos_empresas/', null=True, blank=True)

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
    es_publico = models.BooleanField(default=True)

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
    
class Conexion(models.Model):
    # Seguidor genérico (puede ser un usuario, empresa, etc.)
    seguidor_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="conexiones_realizados", default=1)
    seguidor_object_id = models.PositiveIntegerField(default=1)
    seguidor = GenericForeignKey('seguidor_content_type', 'seguidor_object_id')

    # Seguido genérico (puede ser un usuario, empresa, etc.)
    seguido_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="conexiones", default=1)
    seguido_object_id = models.PositiveIntegerField(default=1)
    seguido = GenericForeignKey('seguido_content_type', 'seguido_object_id')

    fecha_seguimiento = models.DateTimeField(auto_now_add=True)
    
    estado = models.PositiveIntegerField(default=0)
    detalle_conexion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('seguidor_content_type', 'seguidor_object_id', 'seguido_content_type', 'seguido_object_id')

    def __str__(self):
        return f"{self.seguidor} conectó con {self.seguido}"

class ContactoServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name="contactos")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contactos_servicio")

    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    mensaje = models.TextField(blank=True, null=True)

    fecha_contacto = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contacto de {self.nombre} para {self.servicio}"
    
class Noticias(models.Model):
    titulo = models.CharField(max_length=500)
    url = models.URLField(max_length=500)
    url_original = models.URLField(max_length=500, blank=True, null=True)
    medio = models.CharField(max_length=255)
    fecha = models.DateField(blank=True, null=True)
    contenido = models.TextField()
    informe_id = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)  # opcional, para saber cuándo se guardó

    def __str__(self):
        return self.titulo

class Licitacion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='licitaciones_creadas')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField()
    # Puedes agregar estado: activa, cerrada, cancelada...
    estado = models.CharField(max_length=50, choices=[
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
        ('cancelada', 'Cancelada')
    ], default='abierta')
class ArchivoLicitacion(models.Model):
    licitacion = models.ForeignKey(Licitacion, on_delete=models.CASCADE, related_name="archivos_licitacion")
    archivo = models.FileField(upload_to="archivos_licitacion/")

    def __str__(self):
        return self.archivo.name
class OfertaLicitacion(models.Model):
    licitacion = models.ForeignKey(Licitacion, on_delete=models.CASCADE, related_name='ofertas')
    empresa_ofertante = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ofertas_realizadas')
    servicio_ofertado = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='ofertas')
    fecha_oferta = models.DateTimeField(auto_now_add=True)
    mensaje = models.TextField(blank=True)
    # Puede incluir campos como precio estimado, condiciones, etc.

    class Meta:
        unique_together = ('licitacion', 'empresa_ofertante', 'servicio_ofertado')
        
class CargoEmpresa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cargo_empresa")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="cargos_pendientes")
    cargo = models.CharField(max_length=255)
    is_valido = models.BooleanField(default=False)  # False hasta que la empresa lo confirme
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user',)  # Solo un cargo activo por usuario

    def __str__(self):
        estado = "Confirmado" if self.is_valido else "Pendiente"
        return f"{self.user.username} postuló como '{self.cargo}' en {self.empresa.nombre_fantasia} ({estado})"

class Recurso(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fuente = models.CharField(max_length=255, blank=True, null=True)
    rubro = models.CharField(max_length=255, blank=True, null=True)  # antes "tematica"
    link = models.URLField(blank=True, null=True)
    archivo = models.FileField(upload_to='repositorio_recursos/')
    fecha_subida = models.DateTimeField()  # no usamos auto_now_add para aceptar la fecha enviada
    palabrasClaves = models.TextField(default="")
    imagen = models.ImageField(upload_to='imagenes_recursos/', blank=True, null=True) 
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recursos')

    def __str__(self):
        return self.titulo
    
class RecursoUsuarios(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fuente = models.CharField(max_length=255, blank=True, null=True)
    rubro = models.CharField(max_length=255, blank=True, null=True)  # antes "tematica"
    link = models.URLField(blank=True, null=True)
    archivo = models.FileField(upload_to='recursos/')
    fecha_subida = models.DateTimeField()  # no usamos auto_now_add para aceptar la fecha enviada
    palabrasClaves = models.TextField(default="")
    imagen = models.ImageField(upload_to='recursos_imagenes/', blank=True, null=True) 
    
    author_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    author_id = models.PositiveIntegerField()
    author = GenericForeignKey('author_type', 'author_id')
    procesado = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

