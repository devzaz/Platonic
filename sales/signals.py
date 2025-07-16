from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Quotation
from projects.models import Project

@receiver(post_save, sender=Quotation)
def create_project_on_quotation_acceptance(sender, instance, created,**kwargs):
    """
    When a quotation's status is changed to 'accepted', create a new project.
    """

    # We only care about updates where the status is now 'accepted'

    if not created and instance.status == 'accepted':
        # Check if a project for this lead already exists to avoid duplicates
        if not Project.objects.filter(name=instance.lead.description).exists():
            Project.objects.create(
                name = instance.lead.description,
                client = instance.lead.Contact,
                budget = instance.total_amount(),
                project_manager = instance.lead.assign_to,
                status='pending'
            )
            print(f"Project created for accepted quoatation : {instance.quotation_id}")
