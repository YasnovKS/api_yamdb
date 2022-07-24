from rest_framework import permissions
from users.models import ROLES


class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.role == ROLES.admin.name
                or request.user.is_superuser)
