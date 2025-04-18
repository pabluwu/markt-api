# Generated by Django 5.1.6 on 2025-04-07 01:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('markt', '0017_empresa_imagen_perfil'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conexion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seguidor_object_id', models.PositiveIntegerField(default=1)),
                ('seguido_object_id', models.PositiveIntegerField(default=1)),
                ('fecha_seguimiento', models.DateTimeField(auto_now_add=True)),
                ('estado', models.PositiveIntegerField(default=0)),
                ('detalle_conexion', models.CharField(blank=True, max_length=255, null=True)),
                ('seguido_content_type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='conexiones', to='contenttypes.contenttype')),
                ('seguidor_content_type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='conexiones_realizados', to='contenttypes.contenttype')),
            ],
            options={
                'unique_together': {('seguidor_content_type', 'seguidor_object_id', 'seguido_content_type', 'seguido_object_id')},
            },
        ),
    ]
