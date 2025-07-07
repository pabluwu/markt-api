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
from .views.cargo_empresa import CargoEmpresaViewSet
from .views.recurso import RecursoViewSet
from .permissions import IsAuthenticatedOrReadOnlyCustom
from .views.recurso_usuario import RecursoUsuariosViewSet

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
router.register(r'cargo_empresa', CargoEmpresaViewSet, basename='cargo_empresa')
router.register(r'recursos', RecursoViewSet, basename='recurso')
router.register(r'recursos_usuarios', RecursoUsuariosViewSet, basename='recurso_usuarios')


urlpatterns = router.urls + [
    path('search/', GlobalSearchAPIView.as_view(permission_classes=[IsAuthenticatedOrReadOnlyCustom]), name='global-search'),
]