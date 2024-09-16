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
        except AttributeError:
            return False
        
    def has_object_permission(self, request, view):
        try:
            return request.user.hostprofile.can_host_scholarships
        except AttributeError:
            return False

class IsActiveAndCanHostOrIsReviewer(permissions.BasePermission):
    """
    Custom permission to allow PATCH requests if the user is either:
    - An active user who can host sites (IsActivePermission + CanHostSites), OR
    - An active reviewer (IsActivePermission + IsReviewerUser).
    """
    def has_permission(self, request, view):
        # Check if the user is active and can host sites, or if they are an active reviewer
        return (
            (IsActivePermission().has_permission(request, view) and CanHostSites().has_permission(request, view)) or
            (IsActivePermission().has_permission(request, view) and IsReviewerUser().has_permission(request, view))
        )
    
    def has_object_permission(self, request, view, obj):
        # Check for object-level permission using the same logic
        return (
            (IsActivePermission().has_object_permission(request, view, obj) and CanHostSites().has_object_permission(request, view, obj)) or
            (IsActivePermission().has_object_permission(request, view, obj) and IsReviewerUser().has_object_permission(request, view, obj))
        )
