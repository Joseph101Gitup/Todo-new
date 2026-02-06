from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
