import csv
from django.http import StreamingHttpResponse
from django.utils.text import slugify
import logging

logger = logging.getLogger(__name__)

def project_to_csv(project):
    """Generate CSV file for project data"""
    # Validate project object
    if not project:
        logger.error("Project object is None")
        return None
    
    if not hasattr(project, 'id') or not project.id:
        logger.error("Project has no valid ID")
        return None
    
    def row():
        # Header row
        yield ["id", "name", "description", "start_date", "end_date", "duration"]
        
        # Project data row
        yield [
            str(project.id) if project.id else "",
            str(project.name) if project.name else "",
            str(project.description) if project.description else "",
            str(project.start_date) if project.start_date else "",
            str(project.end_date) if project.end_date else "",
            str(project.duration) if project.duration else ""
        ]
        
        # Empty row for separation
        yield []
        
        # Tasks header
        yield ["Tasks:"]
        yield ["id", "title", "status", "due_date"]
        
        # Task rows
        if hasattr(project, 'tasks') and project.tasks.exists():
            for task in project.tasks.all():
                yield [
                    str(task.id) if task.id else "",
                    str(task.title) if task.title else "",
                    str(task.status) if task.status else "",
                    str(task.due_date) if task.due_date else ""
                ]

    # Generate CSV content with proper escaping
    def generate_csv():
        for row_data in row():
            # Handle None values and ensure all items are strings
            processed_row = []
            for item in row_data:
                if item is None:
                    processed_row.append("")
                else:
                    processed_row.append(str(item))
            
            # Join with commas and add newline
            yield ",".join(f'"{item.replace('"', '""')}"' for item in processed_row) + "\n"

    # Create filename
    if project.name:
        filename = f"{slugify(project.name)}.csv"
    else:
        filename = f"project_{project.id}.csv"
    
    # Create streaming response
    response = StreamingHttpResponse(
        generate_csv(),
        content_type="text/csv"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    
    logger.info(f"CSV file generated successfully for project {project.id}")
    return response
