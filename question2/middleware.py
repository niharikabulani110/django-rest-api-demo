import inspect
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    """
    Persists an AuditLog row AFTER each view executes (so we know response status).
    Add this at the *bottom* of MIDDLEWARE so auth / DRF have already run.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        module = view_func.__module__
        view = view_func.__self__.__class__ if hasattr(view_func, "__self__") else view_func
        view_name = f"{module}.{view.__name__}"
        request._audit_action = f"{request.method} {view_name}"
        return None

    def process_response(self, request, response):
        if getattr(request, "user", None) and request.user.is_authenticated:
            AuditLog.objects.create(
                user        = request.user,
                action      = getattr(request, "_audit_action", request.method),
                path        = request.path[:255],
                method      = request.method,
                ip_address  = request.META.get("REMOTE_ADDR"),
                status_code = response.status_code,
                timestamp   = now(),
            )
        return response
