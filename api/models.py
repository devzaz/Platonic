from django.db import models
import uuid

# Create your models here.

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContactUs(BaseModel):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()



class Career(BaseModel):
    position_choices = [
        ('Interior Designer', 'Interior Designer'),
        ('Junior Interior Designer', 'Junior Interior Designer'),
        ('3D Visualizer', '3D Visualizer'),
        ('Architectural Designer', 'Architectural Designer'),
        ('Project Manager', 'Project Manager'),
        ('Site Supervisor', 'Site Supervisor'),
        ('Furniture Designer', 'Furniture Designer'),
        ('Lighting Designer', 'Lighting Designer'),
        ('Drafter(AutoCAD/SketchUp)', 'Drafter(AutoCAD/SketchUp)'),
        ('Client Relations Executive', 'Client Relations Executive'),
    ]
    


    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    portfolio_link = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=250, choices=position_choices)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True, null=True)


