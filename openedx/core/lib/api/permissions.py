from django.conf import settings
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class ApiKeyHeaderPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Check for permissions by matching the configured API key and header

        If settings.DEBUG is True and settings.EDX_API_KEY is not set or None,
        then allow the request. Otherwise, allow the request if and only if
        settings.EDX_API_KEY is set and the X-Edx-Api-Key HTTP header is
        present in the request and matches the setting.
        """
        api_key = getattr(settings, "EDX_API_KEY", None)
        return (
            (settings.DEBUG and api_key is None) or
            (api_key is not None and request.META.get("HTTP_X_EDX_API_KEY") == api_key)
        )


class IsAuthenticatedOrDebug(permissions.BasePermission):
    """
    Allows access only to authenticated users, or anyone if debug mode is enabled.
    """

    def has_permission(self, request, view):
        if settings.DEBUG:
            return True

        # Note: There is a bug in DRF that crops up when this method returns False. Rather than fork DRF,
        # just raise the appropriate exception. See https://github.com/tomchristie/django-rest-framework/issues/1939.
        user = getattr(request, 'user', None)
        if user and user.is_authenticated():
            return True
        else:
            raise PermissionDenied
