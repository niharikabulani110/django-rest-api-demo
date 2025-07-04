from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.http import Http404
import logging
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .utils import project_to_csv

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
def project_list(request):
    if request.method == 'GET':
        projects = Project.objects.filter(is_active=True)
        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            projects = projects.filter(start_date=start_date)
        if end_date:
            projects = projects.filter(end_date=end_date)
        
        search = request.GET.get('search')
        if search:
            projects = projects.filter(name__icontains=search)
        
        ordering = request.GET.get('ordering', '-created_at')
        if ordering:
            projects = projects.order_by(ordering)
        
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            logger.info(f"Project created successfully by user {request.user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def project_detail(request, pk):
    project = Project.objects.filter(pk=pk, is_active=True).first()
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Project {project.id} updated successfully")
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    elif request.method == 'DELETE':
        project.is_active = False
        project.save()
        logger.info(f"Project {project.id} soft deleted successfully")
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def project_bulk_delete(request):
    ids = request.data.get("ids", [])
    
    if not ids:
        return Response(
            {"error": "No project IDs provided for deletion"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not isinstance(ids, list):
        return Response(
            {"error": "Project IDs must be provided as a list"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    for project_id in ids:
        if not isinstance(project_id, int) or project_id <= 0:
            return Response(
                {"error": "All project IDs must be positive integers"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    existing_projects = Project.objects.filter(id__in=ids, is_active=True)
    existing_ids = list(existing_projects.values_list('id', flat=True))
    
    if len(existing_ids) != len(ids):
        missing_ids = set(ids) - set(existing_ids)
        return Response(
            {
                "error": "Some projects not found or already deleted",
                "missing_ids": list(missing_ids),
                "found_ids": existing_ids
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    with transaction.atomic():
        existing_projects.update(is_active=False)
    
    logger.info(f"Bulk deleted {len(existing_ids)} projects: {existing_ids}")
    return Response({
        "message": f"Successfully deleted {len(existing_ids)} projects",
        "deleted": existing_ids
    })

@api_view(['POST'])
@parser_classes([MultiPartParser])
def project_upload_image(request, pk):
    project = Project.objects.filter(pk=pk, is_active=True).first()
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if 'image' not in request.FILES:
        return Response(
            {"error": "No image file provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if image_file.content_type not in allowed_types:
        return Response(
            {
                "error": "Invalid file type",
                "allowed_types": allowed_types,
                "received_type": image_file.content_type
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    max_size = 5 * 1024 * 1024
    if image_file.size > max_size:
        return Response(
            {
                "error": "File too large",
                "max_size_mb": 5,
                "file_size_mb": round(image_file.size / (1024 * 1024), 2)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    project.image = image_file
    project.save()
    
    logger.info(f"Image uploaded successfully for project {project.id}")
    serializer = ProjectSerializer(project)
    return Response(serializer.data)

@api_view(['GET'])
def project_export_csv(request, pk):
    project = Project.objects.filter(pk=pk, is_active=True).first()
    if not project:
        return Response(
            {"error": "Project not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    csv_file = project_to_csv(project)
    if csv_file:
        logger.info(f"CSV exported successfully for project {project.id}")
        return csv_file
    else:
        return Response(
            {"error": "Failed to generate CSV file"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
def task_list(request, project_pk):
    project = Project.objects.filter(id=project_pk, is_active=True).first()
    if not project:
        return Response(
            {"error": "Project not found or inactive"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        tasks = Task.objects.filter(project_id=project_pk)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_id=project_pk)
            logger.info(f"Task created successfully for project {project_pk}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, project_pk, pk):
    project = Project.objects.filter(id=project_pk, is_active=True).first()
    if not project:
        return Response(
            {"error": "Project not found or inactive"},
            status=status.HTTP_404_NOT_FOUND
        )
    task = Task.objects.filter(pk=pk, project_id=project_pk).first()
    if not task:
        return Response(
            {"error": "Task not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Task {task.id} updated successfully")
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    elif request.method == 'DELETE':
        task.delete()
        logger.info(f"Task {task.id} deleted successfully")
        return Response(status=status.HTTP_204_NO_CONTENT)
