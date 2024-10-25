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
    REQUIRED_FIELDS = []

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
