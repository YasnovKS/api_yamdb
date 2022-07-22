from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Global permission to only allow admin users to edit it.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request but other
        # only to the admin user
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False

        return request.user.role == 'admin' or request.user.is_superuser
