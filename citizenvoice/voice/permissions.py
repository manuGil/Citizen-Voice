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


class CanAccessViaShareableLink(permissions.BasePermission):
    """
    Permission to access surveys via shareable link token.
    Validates token, link enabled status, expiration, and authentication requirements.
    """

    def has_permission(self, request, view):
        """View-level permission - allow all, object-level will validate"""
        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if request has valid shareable token for survey access.
        """
        # Get token from URL parameter or request data
        token = None
        if hasattr(view, 'kwargs') and 'token' in view.kwargs:
            token = view.kwargs.get('token')
        elif hasattr(request, 'data') and 'shareable_token' in request.data:
            token = request.data.get('shareable_token')
        elif hasattr(request, 'query_params') and 'shareable_token' in request.query_params:
            token = request.query_params.get('shareable_token')

        if not token:
            return False

        # Validate token matches survey
        if obj.shareable_token != token:
            return False

        # Check if link is enabled
        if not obj.shareable_link_enabled:
            return False

        # Check link expiration
        from django.utils import timezone
        if obj.shareable_link_expires_at and obj.shareable_link_expires_at < timezone.now():
            return False

        # Check survey expiration
        if obj.expire_date < timezone.now():
            return False

        # Check authentication requirement
        if obj.shareable_link_requires_auth:
            if not request.user.is_authenticated:
                return False

        return True


class AllowShareableLinkOrRequireAuth(permissions.BasePermission):
    """
    Permission class for response submission that allows anonymous access
    if a valid shareable token is provided, otherwise requires authentication for POST.
    
    This enables anonymous users to submit responses via shareable links
    when the link doesn't require authentication.
    """

    def has_permission(self, request, view):
        """
        View-level permission check.
        - If shareable_token is provided in request.data, validate it and allow access
          (even for anonymous users if link doesn't require auth)
        - Otherwise, require authentication for POST requests
        """
        # For safe methods (GET, HEAD, OPTIONS), allow by default
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Extract shareable_token and responseId from request data
        # Try multiple ways to access the data since it might not be parsed yet
        shareable_token = None
        response_id = None
        
        # Method 1: Try request.data (DRF property)
        try:
            if hasattr(request, 'data'):
                data = request.data
                if hasattr(data, 'get'):
                    shareable_token = data.get('shareable_token')
                    response_id = data.get('responseId')
                elif isinstance(data, dict):
                    shareable_token = data.get('shareable_token')
                    response_id = data.get('responseId')
        except (AttributeError, TypeError):
            pass
        
        # Method 2: Try parsing request.body manually if data not available
        if not shareable_token and hasattr(request, 'body') and request.body:
            import json
            try:
                body_str = request.body
                if isinstance(body_str, bytes):
                    body_str = body_str.decode('utf-8')
                body_data = json.loads(body_str)
                if isinstance(body_data, dict):
                    shareable_token = body_data.get('shareable_token')
                    response_id = body_data.get('responseId')
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
                pass
        
        if shareable_token:
            # Shareable token provided - validate it
            # We need to get the survey from the responseId
            if not response_id:
                # No responseId, can't validate - require auth
                return request.user.is_authenticated
            
            try:
                from voice.models import Response as ResponseModel, Survey
                from django.utils import timezone
                
                # Get the response to find the survey
                resp = ResponseModel.objects.get(pk=response_id)
                survey = resp.survey
                
                # Validate shareable token
                if survey.shareable_token != shareable_token:
                    return False
                
                if not survey.shareable_link_enabled:
                    return False
                
                # Check link expiration
                if survey.shareable_link_expires_at and survey.shareable_link_expires_at < timezone.now():
                    return False
                
                # Check survey expiration
                if survey.expire_date < timezone.now():
                    return False
                
                # If link requires auth, user must be authenticated
                if survey.shareable_link_requires_auth:
                    return request.user.is_authenticated
                
                # Valid token and link doesn't require auth - allow anonymous access
                return True
                
            except (ResponseModel.DoesNotExist, ValueError, TypeError):
                # Invalid responseId or other error - require auth
                return request.user.is_authenticated
        
        # No shareable token - require authentication for POST
        return request.user.is_authenticated
