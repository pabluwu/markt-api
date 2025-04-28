from rest_framework.routers import DefaultRouter
from .views.user import UsuarioViewSet
from .views.empresa import EmpresaViewSet
from .views.perfil import PerfilViewSet
from .views.post import PostViewSet
from .views.like import LikeViewSet
from .views.seguimiento import SeguimientoViewSet
from .views.comment import CommentViewSet
from .views.servicio import ServicioViewSet
from .views.conexion import ConexionViewSet
from .views.global_search import GlobalSearchAPIView
from .views.contacto_servicio import ContactoServicioViewSet
from .views.noticia import NoticiaViewSet
from .views.licitacion import LicitacionViewSet
from .views.servicio_licitacion import ServicioLicitacionViewSet

from django.urls import path

router = DefaultRouter()
router.register(r'usuario', UsuarioViewSet, basename='usuario')
router.register(r'empresa', EmpresaViewSet, basename='empresa')
router.register(r'perfil', PerfilViewSet, basename='perfil')
router.register(r'post', PostViewSet, basename='post')
router.register(r'like', LikeViewSet, basename='like')
router.register(r'seguir', SeguimientoViewSet, basename='seguimiento')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'conexion', ConexionViewSet, basename='conexion')
router.register(r'contacto_servicio', ContactoServicioViewSet, basename='contacto_servicio')
router.register(r'noticias', NoticiaViewSet, basename='noticia')
router.register(r'licitacion', LicitacionViewSet, basename='licitacion')
router.register(r'servicio_licitacion', ServicioLicitacionViewSet, basename='servicio_licitacion')


urlpatterns = router.urls + [
    path('search/', GlobalSearchAPIView.as_view(), name='global-search'),
]