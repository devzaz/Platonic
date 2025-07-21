from django.db import models
from django.db import models
from django.conf import settings
from projects.models import Project 




class ProjectMilestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=255, help_text="e.g., 'Submit Final Drawings'")
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.name} for {self.project.name}"
    


class BaseDocument(models.Model):
    """An abstract model for common fields in operational documents."""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    document_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # This makes it an abstract base class



class RequestForInformation(BaseDocument):
    # The 'project', 'status', etc. fields are inherited from BaseDocument
    subject = models.CharField(max_length=255)
    question = models.TextField()
    response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"RFI: {self.document_id} for {self.project.name}"
    


class VariationOrder(BaseDocument):
    reason = models.CharField(max_length=255)
    description = models.TextField()
    cost_impact = models.DecimalField(max_digits=12, decimal_places=2, help_text="Positive for addition, negative for omission")
    schedule_impact_days = models.IntegerField(default=0)

    def __str__(self):
        return f"VO: {self.document_id} for {self.project.name}"
    


class InspectionRequest(BaseDocument):
    location = models.CharField(max_length=255, help_text="e.g., 'First Floor Slab'")
    trade = models.CharField(max_length=100, help_text="e.g., 'Concrete Works'")
    inspection_date = models.DateTimeField()
    is_passed = models.BooleanField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"IR: {self.document_id} for {self.project.name}"

class MaterialRequest(BaseDocument):
    # This document links the design/construction needs to the procurement module
    item_description = models.CharField(max_length=255)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, help_text="e.g., 'kg', 'm', 'pcs'")
    required_by_date = models.DateField()

    def __str__(self):
        return f"MR: {self.document_id} for {self.project.name}"