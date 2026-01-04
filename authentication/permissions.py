from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Only allow admin users"""
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin has full access, others have read-only"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions for all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions only for admin
        return request.user.role == 'admin'

class IsOwnerOrReadOnly(BasePermission):
    """Owner has full access, others have read-only"""
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return True
        return obj.user == request.user or request.user.role == 'admin'