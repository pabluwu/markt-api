from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthenticatedOrReadOnlyCustom(BasePermission):
    """
    Permite acceso de lectura a cualquiera, pero requiere autenticación para métodos de escritura.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # GET, HEAD, OPTIONS son públicos
        return request.user and request.user.is_authenticated  # POST, PUT, DELETE requieren login
