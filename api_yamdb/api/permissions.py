from rest_framework import permissions


class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_superuser


class IsProfileOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.username == request.user.username
