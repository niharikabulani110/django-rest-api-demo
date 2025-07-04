# DataX Project - Django REST API with Audit Logging and Image Processing

This project implements three distinct Django applications, each addressing different requirements for a comprehensive web API system.

## 🏗️ Project Overview

The project consists of three main Django apps:
- **Question 1**: Project & Task Management API with CRUD operations
- **Question 2**: Audit Logging System with middleware
- **Question 3**: Image Processing Utility with bulk processing capabilities

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## 🚀 Installation & Setup

1. **Clone the repository and navigate to the project directory:**
   ```bash
   cd datax_project
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional but recommended for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Populate the database with test data:**
   ```bash
   python manage.py populate_test_data
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## 📚 Question 1: Project & Task Management API

### Implementation Overview

**Location**: `question1/` directory

**Key Features**:
- Full CRUD operations for Projects and Tasks
- Nested resource structure (Tasks belong to Projects)
- Image upload functionality for projects
- CSV export capability
- Bulk delete operations
- Advanced filtering and search
- Soft delete implementation

### Data Models

#### Project Model (`question1/models.py`)
```python
class Project(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.PositiveIntegerField(editable=False)  # Auto-calculated
    image = models.ImageField(upload_to="projects/", blank=True)
    is_active = models.BooleanField(default=True)  # Soft delete
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Task Model (`question1/models.py`)
```python
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[("todo","To-Do"),("ip","In-Progress"),("done","Done")])
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects/` | List all active projects |
| POST | `/api/projects/` | Create a new project |
| GET | `/api/projects/{id}/` | Get project details |
| PUT | `/api/projects/{id}/` | Update project |
| DELETE | `/api/projects/{id}/` | Soft delete project |
| POST | `/api/projects/bulk-delete/` | Bulk delete projects |
| POST | `/api/projects/{id}/upload-image/` | Upload project image |
| GET | `/api/projects/{id}/export-csv/` | Export project data to CSV |
| GET | `/api/projects/{project_id}/tasks/` | List tasks for a project |
| POST | `/api/projects/{project_id}/tasks/` | Create a new task |
| GET | `/api/projects/{project_id}/tasks/{id}/` | Get task details |
| PUT | `/api/projects/{project_id}/tasks/{id}/` | Update task |
| DELETE | `/api/projects/{project_id}/tasks/{id}/` | Delete task |

### Demo Instructions

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Access the API endpoints using curl or a tool like Postman:**

   **List all projects:**
   ```bash
   curl -X GET http://localhost:8000/api/projects/ \
     -H "Authorization: Basic $(echo -n 'testuser:testpass123' | base64)"
   ```

   **Create a new project:**
   ```bash
   curl -X POST http://localhost:8000/api/projects/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic $(echo -n 'testuser:testpass123' | base64)" \
     -d '{
       "name": "New Test Project",
       "description": "A test project for demonstration",
       "start_date": "2024-01-01",
       "end_date": "2024-12-31"
     }'
   ```

   **Upload an image to a project:**
   ```bash
   curl -X POST http://localhost:8000/api/projects/1/upload-image/ \
     -H "Authorization: Basic $(echo -n 'testuser:testpass123' | base64)" \
     -F "image=@/path/to/your/image.jpg"
   ```

   **Export project to CSV:**
   ```bash
   curl -X GET http://localhost:8000/api/projects/1/export-csv/ \
     -H "Authorization: Basic $(echo -n 'testuser:testpass123' | base64)" \
     --output project_export.csv
   ```

3. **Query Parameters for Filtering:**
   - `?search=keyword` - Search projects by name
   - `?start_date=2024-01-01` - Filter by start date
   - `?end_date=2024-12-31` - Filter by end date
   - `?ordering=-created_at` - Sort by creation date (descending)

## 📊 Question 2: Audit Logging System

### Implementation Overview

**Location**: `question2/` directory

**Key Features**:
- Automatic logging of all authenticated HTTP requests
- Middleware-based implementation for seamless integration
- Admin-only access to audit logs
- Comprehensive request metadata capture
- Database indexing for performance

### Data Model

#### AuditLog Model (`question2/models.py`)
```python
class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=180)  # e.g., "GET question1.views.ProjectViewSet.list"
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=8)
    ip_address = models.GenericIPAddressField(null=True)
    status_code = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Middleware Implementation

The `AuditMiddleware` (`question2/middleware.py`) automatically logs all authenticated requests:

```python
class AuditMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Capture view information
        module = view_func.__module__
        view = view_func.__self__.__class__ if hasattr(view_func, "__self__") else view_func
        view_name = f"{module}.{view.__name__}"
        request._audit_action = f"{request.method} {view_name}"
        return None

    def process_response(self, request, response):
        # Log authenticated requests
        if getattr(request, "user", None) and request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=getattr(request, "_audit_action", request.method),
                path=request.path[:255],
                method=request.method,
                ip_address=request.META.get("REMOTE_ADDR"),
                status_code=response.status_code,
                timestamp=now(),
            )
        return response
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/audit/audit-logs/` | List all audit logs (admin only) |
| GET | `/api/audit/audit-logs/{id}/` | Get specific audit log (admin only) |

### Demo Instructions

1. **Access the Django admin interface:**
   - Go to `http://localhost:8000/admin/`
   - Login with your superuser credentials

2. **View audit logs in admin:**
   - Navigate to "Question2" → "Audit logs"
   - You'll see all logged requests with timestamps, users, and actions

3. **Generate audit logs by making API requests:**
   ```bash
   # Make some API calls to generate audit logs
   curl -X GET http://localhost:8000/api/projects/ \
     -H "Authorization: Basic $(echo -n 'testuser:testpass123' | base64)"
   
   curl -X POST http://localhost:8000/api/projects/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic $(echo -n 'testuser:testpass123' | base64)" \
     -d '{"name": "Test", "start_date": "2024-01-01", "end_date": "2024-12-31"}'
   ```

4. **View the audit logs via API (admin only):**
   ```bash
   curl -X GET http://localhost:8000/api/audit/audit-logs/ \
     -H "Authorization: Basic $(echo -n 'admin:adminpassword' | base64)"
   ```

## 🖼️ Question 3: Image Processing Utility

### Implementation Overview

**Location**: `question3/` directory

**Key Features**:
- Bulk image processing from URLs or CSV files
- Image metadata extraction
- Thumbnail generation
- Base64 encoding for both original and thumbnail images
- Error handling and validation
- Progress tracking with tqdm

### Core Functions

#### Image Processing (`question3/utils.py`)
```python
def process_url(url: str) -> Dict:
    """Process a single image URL and return metadata + base64 data"""
    # Downloads image, extracts metadata, generates thumbnail
    # Returns comprehensive image information
```

#### Management Command (`question3/management/commands/process_images.py`)
```python
class Command(BaseCommand):
    """Bulk-process images from URLs or CSV files"""
    # Supports --url for single URL or --csv for batch processing
    # Outputs JSON with processing results
```

### Demo Instructions

1. **Process a single image URL:**
   ```bash
   python manage.py process_images --url https://picsum.photos/800/600
   ```

2. **Process multiple images from a CSV file:**
   ```bash
   # Create a CSV file with image URLs
   echo "https://picsum.photos/800/600" > images.csv
   echo "https://picsum.photos/400/300" >> images.csv
   
   # Process the CSV
   python manage.py process_images --csv images.csv
   ```

3. **Specify custom output file:**
   ```bash
   python manage.py process_images --url https://picsum.photos/800/600 --out my_results.json
   ```

4. **View the output JSON file:**
   ```bash
   cat output_*.json
   ```

   The output contains:
   ```json
   {
     "image_url": "https://picsum.photos/800/600",
     "status": "success",
     "original_size": 12345,
     "original_format": "JPEG",
     "original_resolution": "800x600",
     "original_base64": "base64_encoded_original_image",
     "thumb_size": 5432,
     "thumb_resolution": "320x240",
     "thumb_base64": "base64_encoded_thumbnail"
   }
   ```

## 🔧 Configuration

### Django Settings (`datax_project/settings.py`)

Key configurations:
- **REST Framework**: Configured with authentication, pagination, and filtering
- **Media Files**: Configured for image uploads
- **Middleware**: Audit middleware added for automatic logging
- **Database**: SQLite for development (easily changeable to PostgreSQL/MySQL)

### Authentication

The API uses Django REST Framework's authentication classes:
- Session Authentication
- Basic Authentication
- Token Authentication

Default test credentials:
- Username: `testuser`
- Password: `testpass123`

## 🧪 Testing

### Running Tests
```bash
python manage.py test
```

### Manual Testing
1. Use the provided test data: `python manage.py populate_test_data`
2. Test API endpoints with curl or Postman
3. Verify audit logs in Django admin
4. Test image processing with various URLs

## 📁 Project Structure

```
datax_project/
├── datax_project/          # Main Django project
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── question1/              # Project & Task Management
│   ├── models.py          # Project and Task models
│   ├── views.py           # API views and endpoints
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # URL routing
│   ├── utils.py           # CSV export utilities
│   └── management/        # Custom management commands
│       └── commands/
│           └── populate_test_data.py
├── question2/              # Audit Logging System
│   ├── models.py          # AuditLog model
│   ├── views.py           # Audit log views
│   ├── middleware.py      # Audit middleware
│   ├── serializers.py     # DRF serializers
│   └── urls.py            # URL routing
├── question3/              # Image Processing Utility
│   ├── utils.py           # Image processing functions
│   └── management/        # Custom management commands
│       └── commands/
│           └── process_images.py
├── media/                  # Uploaded files
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
└── README.md              # This file
```