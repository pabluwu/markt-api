from rest_framework import serializers
from ..models import Servicio, ProductoServicio, Region, FormaPago, ModalidadAtencion, Empresa

# Serializador para los productos del servicio
class ProductoServicioSerializer(serializers.ModelSerializer):
    # Asegurándonos de que el precio estimado sea un número decimal
    precio_estimado = serializers.DecimalField(max_digits=10, decimal_places=2)
    id = serializers.IntegerField(required=False)
    # Asegurándonos de que la disponibilidad geográfica sea una lista de regiones válidas
    # disponibilidad_geografica = serializers.SlugRelatedField(slug_field='nombre', queryset=Region.objects.all(), many=True)

    class Meta:
        model = ProductoServicio
        fields = ['id','nombre', 'descripcion_breve', 'unidad_venta', 'precio_estimado']


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
        fields = ['id','descripcion', 'tiempo_entrega', 'modalidades_atencion', 'formas_pago', 'certificaciones', 'productos', 'empresa', 'contacto_nombre', 'contacto_cargo', 'contacto_email', 'contacto_telefono', 'contacto_web']

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
    
    def update(self, instance, validated_data):
        productos_data = validated_data.pop('productos', [])
        modalidades_data = validated_data.pop('modalidades_atencion', [])
        formas_pago_data = validated_data.pop('formas_pago', [])

        # Actualizar campos simples del servicio
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar relaciones many-to-many
        if modalidades_data:
            instance.modalidades_atencion.set(modalidades_data)
        if formas_pago_data:
            instance.formas_pago.set(formas_pago_data)

        # Sincronizar productos (borrado, actualización o creación)
        existing_productos = {p.id: p for p in instance.productos.all()}

        for producto_data in productos_data:
            producto_id = producto_data.get("id")
            if producto_id and producto_id in existing_productos:
                # Si existe, actualizar
                producto = existing_productos.pop(producto_id)
                for attr, value in producto_data.items():
                    setattr(producto, attr, value)
                producto.save()
            else:
                # Si no existe, crear uno nuevo
                ProductoServicio.objects.create(servicio=instance, **producto_data)

        # Eliminar productos que no fueron enviados en la actualización
        for producto in existing_productos.values():
            producto.delete()

        return instance

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nombre_empresa', 'nombre_fantasia', 'rut', 'activa', 'imagen_perfil']
        
class ServicioDetalleSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer()
    productos = ProductoServicioSerializer(many=True)

    class Meta:
        model = Servicio
        fields = [
            'id',
            'descripcion',
            'tiempo_entrega',
            'certificaciones',
            'contacto_nombre',
            'contacto_cargo',
            'contacto_email',
            'contacto_telefono',
            'contacto_web',
            'modalidades_atencion',
            'formas_pago',
            'empresa',
            'productos'
        ]