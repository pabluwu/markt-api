from rest_framework.routers import DefaultRouter
from .views.user import UsuarioViewSet
from .views.empresa import EmpresaViewSet
from .views.perfil import PerfilViewSet
from .views.post import PostViewSet
from .views.like import LikeViewSet

router = DefaultRouter()
router.register(r'usuario', UsuarioViewSet, basename='usuario')
router.register(r'empresa', EmpresaViewSet, basename='empresa')
router.register(r'perfil', PerfilViewSet, basename='perfil')
router.register(r'post', PostViewSet, basename='post')
router.register(r'like', LikeViewSet, basename='like')

urlpatterns = router.urls