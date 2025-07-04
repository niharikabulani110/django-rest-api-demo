from django.urls import path
from .views import (
    project_list, project_detail, project_bulk_delete, 
    project_upload_image, project_export_csv,
    task_list, task_detail
)

urlpatterns = [
    # Project URLs
    path('projects/', project_list, name='project-list'),
    path('projects/bulk-delete/', project_bulk_delete, name='project-bulk-delete'),
    path('projects/<int:pk>/', project_detail, name='project-detail'),
    path('projects/<int:pk>/upload-image/', project_upload_image, name='project-upload-image'),
    path('projects/<int:pk>/export-csv/', project_export_csv, name='project-export-csv'),
    
    path('projects/<int:project_pk>/tasks/', task_list, name='task-list'),
    path('projects/<int:project_pk>/tasks/<int:pk>/', task_detail, name='task-detail'),
]
