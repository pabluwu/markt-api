# Generated by Django 5.1.6 on 2025-06-30 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("markt", "0032_alter_empresa_comuna_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="empresa",
            name="telefono_empresa",
            field=models.BigIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="empresa",
            name="telefono_representante_legal",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
