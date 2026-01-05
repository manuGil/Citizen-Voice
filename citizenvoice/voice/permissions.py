from rest_framework import permissions


class IsAuthenticatedAndSelfOrMakeReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
            return True
        if not request.user.is_authenticated:
            return False
        return obj.designer == request.user


class IsAuthenticatedAndSelf(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj.designer == request.user


class CanAccessSurvey(permissions.BasePermission):
    """
    Permission to access surveys:
    - Public surveys (need_logged_user=False): anyone can access
    - Private surveys (need_logged_user=True): only designer can access
    - Unpublished surveys: only designer can access
    
    For write operations (PUT, PATCH, DELETE), only the designer can modify.
    """

    def has_permission(self, request, view):
        """
        View-level permission check.
        Allow all requests at view level - object-level permissions will handle access control.
        This ensures we return 403 (Forbidden) instead of 401 (Unauthorized) when appropriate.
        """
        return True

    def has_object_permission(self, request, view, obj):
        # For write operations, only designer can modify
        if request.method not in permissions.SAFE_METHODS:
            if not request.user.is_authenticated:
                return False
            return obj.designer == request.user
        
        # For read operations (GET, HEAD, OPTIONS)
        # Public surveys are accessible to everyone
        if not obj.need_logged_user and obj.is_published:
            return True
        
        # Unpublished surveys: only designer can access
        if not obj.is_published:
            if not request.user.is_authenticated:
                return False
            return obj.designer == request.user
        
        # Private surveys require authentication and ownership
        if obj.need_logged_user:
            if not request.user.is_authenticated:
                return False
            return obj.designer == request.user
        
        # Default: deny access
        return False
