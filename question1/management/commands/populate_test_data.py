from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random
from question1.models import Project, Task

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with test projects and tasks'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create a test user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': True,
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Created test user: {user.username}')
        else:
            self.stdout.write(f'Using existing user: {user.username}')

        # Sample project data
        projects_data = [
            {
                'name': 'E-commerce Website Development',
                'description': 'Build a modern e-commerce platform with React frontend and Django backend',
                'start_date': date(2024, 1, 15),
                'end_date': date(2024, 6, 30),
            },
            {
                'name': 'Mobile App for Food Delivery',
                'description': 'Develop a cross-platform mobile application for food delivery service',
                'start_date': date(2024, 2, 1),
                'end_date': date(2024, 8, 15),
            },
            {
                'name': 'Data Analytics Dashboard',
                'description': 'Create a comprehensive dashboard for business analytics and reporting',
                'start_date': date(2024, 3, 10),
                'end_date': date(2024, 7, 20),
            },
            {
                'name': 'Inventory Management System',
                'description': 'Build a web-based inventory management system for retail stores',
                'start_date': date(2024, 1, 1),
                'end_date': date(2024, 5, 31),
            },
            {
                'name': 'Customer Relationship Management',
                'description': 'Develop a CRM system to manage customer interactions and sales pipeline',
                'start_date': date(2024, 4, 1),
                'end_date': date(2024, 9, 30),
            },
            {
                'name': 'Learning Management System',
                'description': 'Create an online learning platform for educational institutions',
                'start_date': date(2024, 2, 15),
                'end_date': date(2024, 8, 31),
            },
            {
                'name': 'Healthcare Appointment System',
                'description': 'Build a system for managing patient appointments and medical records',
                'start_date': date(2024, 3, 1),
                'end_date': date(2024, 7, 15),
            },
            {
                'name': 'Real Estate Management Platform',
                'description': 'Develop a platform for managing real estate listings and client interactions',
                'start_date': date(2024, 1, 20),
                'end_date': date(2024, 6, 15),
            },
        ]

        # Sample task data for each project
        tasks_data = [
            # E-commerce Website
            [
                {'title': 'Design UI/UX mockups', 'status': 'done', 'due_date': date(2024, 2, 15)},
                {'title': 'Set up Django backend', 'status': 'done', 'due_date': date(2024, 3, 1)},
                {'title': 'Implement user authentication', 'status': 'ip', 'due_date': date(2024, 3, 15)},
                {'title': 'Create product catalog', 'status': 'ip', 'due_date': date(2024, 4, 1)},
                {'title': 'Implement shopping cart', 'status': 'todo', 'due_date': date(2024, 4, 15)},
                {'title': 'Payment integration', 'status': 'todo', 'due_date': date(2024, 5, 1)},
                {'title': 'Testing and bug fixes', 'status': 'todo', 'due_date': date(2024, 6, 15)},
            ],
            # Mobile App
            [
                {'title': 'Market research and analysis', 'status': 'done', 'due_date': date(2024, 2, 15)},
                {'title': 'Design app wireframes', 'status': 'done', 'due_date': date(2024, 3, 1)},
                {'title': 'Set up React Native project', 'status': 'ip', 'due_date': date(2024, 3, 15)},
                {'title': 'Implement user registration', 'status': 'ip', 'due_date': date(2024, 4, 1)},
                {'title': 'Restaurant listing feature', 'status': 'todo', 'due_date': date(2024, 4, 15)},
                {'title': 'Order tracking system', 'status': 'todo', 'due_date': date(2024, 5, 15)},
                {'title': 'Push notifications', 'status': 'todo', 'due_date': date(2024, 6, 1)},
                {'title': 'App store submission', 'status': 'todo', 'due_date': date(2024, 7, 15)},
            ],
            # Data Analytics Dashboard
            [
                {'title': 'Define KPIs and metrics', 'status': 'done', 'due_date': date(2024, 3, 20)},
                {'title': 'Design dashboard layout', 'status': 'done', 'due_date': date(2024, 4, 1)},
                {'title': 'Set up data pipeline', 'status': 'ip', 'due_date': date(2024, 4, 15)},
                {'title': 'Create data visualization components', 'status': 'ip', 'due_date': date(2024, 5, 1)},
                {'title': 'Implement real-time updates', 'status': 'todo', 'due_date': date(2024, 5, 15)},
                {'title': 'User access controls', 'status': 'todo', 'due_date': date(2024, 6, 1)},
                {'title': 'Performance optimization', 'status': 'todo', 'due_date': date(2024, 6, 15)},
            ],
            # Inventory Management
            [
                {'title': 'Database schema design', 'status': 'done', 'due_date': date(2024, 1, 15)},
                {'title': 'User interface design', 'status': 'done', 'due_date': date(2024, 2, 1)},
                {'title': 'Product management module', 'status': 'done', 'due_date': date(2024, 2, 15)},
                {'title': 'Stock tracking system', 'status': 'ip', 'due_date': date(2024, 3, 1)},
                {'title': 'Barcode scanning integration', 'status': 'ip', 'due_date': date(2024, 3, 15)},
                {'title': 'Reporting and analytics', 'status': 'todo', 'due_date': date(2024, 4, 15)},
                {'title': 'User training and documentation', 'status': 'todo', 'due_date': date(2024, 5, 15)},
            ],
            # CRM System
            [
                {'title': 'Requirements gathering', 'status': 'done', 'due_date': date(2024, 4, 15)},
                {'title': 'System architecture design', 'status': 'done', 'due_date': date(2024, 5, 1)},
                {'title': 'Customer database setup', 'status': 'ip', 'due_date': date(2024, 5, 15)},
                {'title': 'Lead management module', 'status': 'ip', 'due_date': date(2024, 6, 1)},
                {'title': 'Sales pipeline tracking', 'status': 'todo', 'due_date': date(2024, 6, 15)},
                {'title': 'Email integration', 'status': 'todo', 'due_date': date(2024, 7, 15)},
                {'title': 'Reporting dashboard', 'status': 'todo', 'due_date': date(2024, 8, 15)},
                {'title': 'User training', 'status': 'todo', 'due_date': date(2024, 9, 15)},
            ],
            # Learning Management System
            [
                {'title': 'Educational content planning', 'status': 'done', 'due_date': date(2024, 3, 1)},
                {'title': 'Course structure design', 'status': 'done', 'due_date': date(2024, 3, 15)},
                {'title': 'User authentication system', 'status': 'ip', 'due_date': date(2024, 4, 1)},
                {'title': 'Course creation interface', 'status': 'ip', 'due_date': date(2024, 4, 15)},
                {'title': 'Video streaming integration', 'status': 'todo', 'due_date': date(2024, 5, 15)},
                {'title': 'Assignment submission system', 'status': 'todo', 'due_date': date(2024, 6, 15)},
                {'title': 'Progress tracking', 'status': 'todo', 'due_date': date(2024, 7, 15)},
                {'title': 'Mobile app development', 'status': 'todo', 'due_date': date(2024, 8, 15)},
            ],
            # Healthcare System
            [
                {'title': 'HIPAA compliance review', 'status': 'done', 'due_date': date(2024, 3, 15)},
                {'title': 'Patient database design', 'status': 'done', 'due_date': date(2024, 4, 1)},
                {'title': 'Appointment scheduling system', 'status': 'ip', 'due_date': date(2024, 4, 15)},
                {'title': 'Patient portal development', 'status': 'ip', 'due_date': date(2024, 5, 1)},
                {'title': 'Medical records management', 'status': 'todo', 'due_date': date(2024, 5, 15)},
                {'title': 'Billing integration', 'status': 'todo', 'due_date': date(2024, 6, 15)},
                {'title': 'Security audit', 'status': 'todo', 'due_date': date(2024, 7, 1)},
            ],
            # Real Estate Platform
            [
                {'title': 'Market analysis', 'status': 'done', 'due_date': date(2024, 2, 1)},
                {'title': 'Property listing system', 'status': 'done', 'due_date': date(2024, 2, 15)},
                {'title': 'Search and filter functionality', 'status': 'ip', 'due_date': date(2024, 3, 1)},
                {'title': 'Virtual tour integration', 'status': 'ip', 'due_date': date(2024, 3, 15)},
                {'title': 'Client management system', 'status': 'todo', 'due_date': date(2024, 4, 15)},
                {'title': 'Document management', 'status': 'todo', 'due_date': date(2024, 5, 15)},
                {'title': 'Mobile responsive design', 'status': 'todo', 'due_date': date(2024, 6, 1)},
            ],
        ]

        # Create projects and tasks
        created_projects = []
        for i, project_data in enumerate(projects_data):
            project = Project.objects.create(
                name=project_data['name'],
                description=project_data['description'],
                start_date=project_data['start_date'],
                end_date=project_data['end_date'],
                created_by=user
            )
            created_projects.append(project)
            self.stdout.write(f'Created project: {project.name}')

            # Create tasks for this project
            for task_data in tasks_data[i]:
                task = Task.objects.create(
                    project=project,
                    title=task_data['title'],
                    status=task_data['status'],
                    due_date=task_data['due_date'],
                    description=f"Task for {project.name}: {task_data['title']}"
                )
                self.stdout.write(f'  - Created task: {task.title} ({task.status})')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(created_projects)} projects with tasks!'
            )
        )
        self.stdout.write('Test data is ready for API testing.')