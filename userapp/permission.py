from rest_framework import permissions

class IsActivePermission(permissions.BasePermission):  
    def has_permission(self, request,view):
        return request.user.is_active and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_active and request.user.is_authenticated



class IsVerfiedPermission(permissions.BasePermission):
    def has_permission(self, request,view):
        return request.user.userprofile.is_email_verified and request.user.userprofile.is_phone_number_verified
    def has_object_permission(self, request,view, obj):
        return request.user.userprofile.is_email_verified and request.user.userprofile.is_phone_number_verified
    
class IsPremiumUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.premium_account_privilages
    def has_object_permission(self, request, view):
        return request.user.userprofile.premium_account_privilages
    
class IsReviewerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.is_reviewer
    def has_object_permission(self, request, view):
        return request.user.userprofile.is_reviewer

class CanHostSites(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.hostprofile.can_host_scholarships
        except:
            return False
        
    def has_object_permission(self, request, view):
        try:
            return request.user.hostprofile.can_host_scholarships
        except:
            return False