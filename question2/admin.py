from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display   = ("timestamp", "user", "method", "status_code", "path")
    list_filter    = ("method", "status_code")
    search_fields  = ("path", "action", "user__username")
    date_hierarchy = "timestamp"
