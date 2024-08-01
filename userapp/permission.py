from rest_framework import permissions

class IsActivePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_active and request.user.is_authenticated