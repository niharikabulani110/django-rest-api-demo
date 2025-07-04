from django.db import models
from django.contrib.auth import get_user_model


class AuditLog(models.Model):
    """
    One immutable row per authenticated HTTP request.
    """
    user        = models.ForeignKey(
        get_user_model(),
        null=True, blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    action      = models.CharField(    
        max_length=180,
        help_text="e.g. GET question1.views.ProjectViewSet.list",
    )
    path        = models.CharField(max_length=255)          
    method      = models.CharField(max_length=8)             
    ip_address  = models.GenericIPAddressField(null=True)    
    status_code = models.PositiveSmallIntegerField()         
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes  = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.user} {self.method} {self.path}"
