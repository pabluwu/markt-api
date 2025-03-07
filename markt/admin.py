from django.contrib import admin
from .models import Empresa, Perfil, Post


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre_empresa', 'activa', 'fecha_creacion')  # Campos visibles en la lista
    search_fields = ('rut', 'nombre_empresa', 'nombre_fantasia')  # Campos de búsqueda
    list_filter = ('activa',)  # Filtros laterales
    ordering = ('-fecha_creacion',)  # Ordenar por fecha de creación descendente
    
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'empresa')
    
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('content', 'author_id')