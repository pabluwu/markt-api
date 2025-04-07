from rest_framework import serializers
from ..models import Servicio, ProductoServicio, Region, FormaPago, ModalidadAtencion, Empresa

# Serializador para los productos del servicio
class ProductoServicioSerializer(serializers.ModelSerializer):
    # Asegurándonos de que el precio estimado sea un número decimal
    precio_estimado = serializers.DecimalField(max_digits=10, decimal_places=2)
    # Asegurándonos de que la disponibilidad geográfica sea una lista de regiones válidas
    # disponibilidad_geografica = serializers.SlugRelatedField(slug_field='nombre', queryset=Region.objects.all(), many=True)

    class Meta:
        model = ProductoServicio
        fields = ['nombre', 'descripcion_breve', 'unidad_venta', 'precio_estimado', ]


# Serializador para el servicio
class ServicioSerializer(serializers.ModelSerializer):
    productos = ProductoServicioSerializer(many=True)
    
    # Añadimos el campo empresa que tomará el ID de la empresa
    empresa = serializers.PrimaryKeyRelatedField(queryset=Empresa.objects.all())
    
    # Convertimos los valores de modalidades y formas de pago a las instancias correspondientes
    modalidades_atencion = serializers.SlugRelatedField(slug_field='nombre', queryset=ModalidadAtencion.objects.all(), many=True)
    formas_pago = serializers.SlugRelatedField(slug_field='nombre', queryset=FormaPago.objects.all(), many=True)

    class Meta:
        model = Servicio
        fields = ['descripcion', 'tiempo_entrega', 'modalidades_atencion', 'formas_pago', 'certificaciones', 'productos', 'empresa', 'contacto_nombre', 'contacto_cargo', 'contacto_email', 'contacto_telefono', 'contacto_web']

    def create(self, validated_data):
        # Extraemos los productos, modalidades y formas de pago
        productos_data = validated_data.pop('productos')
        modalidades_data = validated_data.pop('modalidades_atencion')
        formas_pago_data = validated_data.pop('formas_pago')

        # Creamos el servicio con los datos validados
        servicio = Servicio.objects.create(**validated_data)

        # Asignamos las modalidades de atención y las formas de pago al servicio
        servicio.modalidades_atencion.set(modalidades_data)
        servicio.formas_pago.set(formas_pago_data)

        # Creamos los productos y los asociamos al servicio
        for producto_data in productos_data:
            producto = ProductoServicio.objects.create(servicio=servicio, **producto_data)

        return servicio
