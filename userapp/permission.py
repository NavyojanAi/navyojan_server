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
        is_active = request.user.is_active and request.user.is_authenticated
        
        can_host_sites = hasattr(request.user, 'can_host_sites') and request.user.can_host_sites
        is_reviewer = hasattr(request.user, 'is_reviewer') and request.user.is_reviewer
        
        return (
            (is_active and can_host_sites) or
            (is_active and is_reviewer)
        )
    
    def has_object_permission(self, request, view, obj):
        is_active = request.user.is_active and request.user.is_authenticated
        
        can_host_sites = hasattr(request.user, 'can_host_sites') and request.user.can_host_sites
        is_reviewer = hasattr(request.user, 'is_reviewer') and request.user.is_reviewer
        
        return (
            (is_active and can_host_sites) or
            (is_active and is_reviewer)
        )

