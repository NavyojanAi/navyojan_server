from rest_framework import permissions

class IsActivePermission(permissions.BasePermission):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated

    def has_object_permission(self, request):
        return request.user.is_active and request.user.is_authenticated


class IsVerfiedPermission(permissions.BasePermission):
    def has_permission(self, request):
        return request.user.userprofile.is_email_verified and request.user.userprofile.is_phone_number_verified
    def has_object_permission(self, request):
        return request.user.userprofile.is_email_verified and request.user.userprofile.is_phone_number_verified