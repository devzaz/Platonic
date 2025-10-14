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




# for project portfolio forntend


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    


class Project(BaseModel):
    Status_Choices = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(default='N/A', blank=True, null=True)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status_Choices, default='completed')
    year = models.PositiveIntegerField()


    def __str__(self):
        return self.title 
    


class ProjectImage(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')


    def __str__(self):
        return f"Image for {self.project.title}"
    


class ProjectVideo(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='project_videos/')


    def __str__(self):
        return f"Video for {self.project.title}"