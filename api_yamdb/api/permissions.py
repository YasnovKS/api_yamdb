from rest_framework import permissions

from users.models import ROLE


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Global permission to only allow admin users to edit it.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request but other
        # only to the admin user
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == ROLE.admin.name
        )
