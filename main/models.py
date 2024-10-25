from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=128, name='username', verbose_name='Username')
    REQUIRED_FIELDS = []

    USERNAME_FIELD = 'email'

    workspaces = models.ManyToManyField('Workspace', related_name='members')
    role = models.CharField(max_length=100, null=True)


class Workspace(BaseModel):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')

    industry = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)

    class Meta:
        db_table = 'workspace'
        indexes = [
            models.Index(fields=['name']),
        ]
        ordering = ['name']


class PostType(models.TextChoices):
    image = 'image', 'Image'
    video = 'video', 'Video'
    text = 'text', 'Text'


class Post(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='events')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    schedule_time = models.DateTimeField()
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_events')
    post_type = models.CharField(max_length=100, choices=PostType.choices)
    post_image = models.ImageField(null=True)
    post_text = models.TextField(null=True)
    post_video = models.FileField(null=True)

    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)

    description = models.TextField(null=True)
    user_notes = models.TextField(null=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'event'
        indexes = [
            models.Index(fields=['schedule_time']),
            models.Index(fields=['is_completed']),
            models.Index(fields=['is_deleted']),
        ]
        ordering = ['schedule_time']

class Reminder(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField()
    is_notified = models.BooleanField(default=False)
    snooze_time = models.DateTimeField(null=True)

    class Meta:
        db_table = 'reminder'
        indexes = [
            models.Index(fields=['reminder_time']),
            models.Index(fields=['is_notified']),
            models.Index(fields=['snooze_time']),
        ]
        ordering = ['reminder_time']
