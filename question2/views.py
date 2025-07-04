from rest_framework import mixins, permissions, viewsets
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    GET /audit-logs/         – list (paginated)
    GET /audit-logs/<pk>/    – detail
    """
    queryset           = AuditLog.objects.select_related("user")
    serializer_class   = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]      # tweak if needed
    ordering           = ["-timestamp"]
