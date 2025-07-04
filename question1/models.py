from django.db import models
from django.contrib.auth import get_user_model

class Project(models.Model):
    name        = models.CharField(max_length=150, db_index=True)
    description = models.TextField(blank=True)
    start_date  = models.DateField()
    end_date    = models.DateField()
    duration    = models.PositiveIntegerField(editable=False)  # autocalc
    image       = models.ImageField(upload_to="projects/", blank=True)
    is_active   = models.BooleanField(default=True)  # “soft delete”

    created_by  = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="projects"
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.duration = (self.end_date - self.start_date).days
        super().save(*args, **kwargs)


class Task(models.Model):
    project     = models.ForeignKey(Project, on_delete=models.CASCADE,
                                    related_name="tasks")
    title       = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20,
                                   choices=[("todo","To-Do"),("ip","In-Progress"),
                                            ("done","Done")],
                                   default="todo")
    due_date    = models.DateField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
