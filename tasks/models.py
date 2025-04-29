from django.db import models
from django.contrib.auth.models import User

# Custom QuerySet
class TaskQuerySet(models.QuerySet):
    def completed(self):
        return self.filter(status='COMPLETED')
    
    def in_progress(self):
        return self.filter(status='IN_PROGRESS')
    
    def pending(self):
        return self.filter(status='PENDING')
    
    def assigned_to(self, user):
        return self.filter(assigned_to=user)

# Custom Manager
class TaskManager(models.Manager):
    def get_queryset(self):
        return TaskQuerySet(self.model, using=self._db)
    
    def completed(self):
        return self.get_queryset().completed()
    
    def in_progress(self):
        return self.get_queryset(). in_progress()
    
    def pending(self):
        return self.get_queryset().pending()
    
    def assigned_to(self, user):
        return self.get_queryset().assigned_to(user)

class Task(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed')
    ]
    project = models.ForeignKey("Project", on_delete=models.CASCADE, default=1)
    assigned_to = models.ManyToManyField(User, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaskManager()  # Use custom manager

    def __str__(self):
        return self.title

class TaskDetail(models.Model):
    HIGH = 'H'
    MEDIUM = 'M'
    LOW = 'L'
    PRIORITY_OPTIONS = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low')
    )
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='details')
    priority = models.CharField(max_length=1, choices=PRIORITY_OPTIONS, default=LOW)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details for Task {self.task.title}"

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()

    def __str__(self):
        return self.name
