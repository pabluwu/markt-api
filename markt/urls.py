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

urlpatterns = router.urls