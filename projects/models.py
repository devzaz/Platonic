from django.db import models
from django.conf import settings
from sales.models import Contact
from core.models import ChartOfAccounts


class Project(models.Model):
    """
    Represents a single construction/ architecture project
    """

    PHASE_CHOICES = (
        ('pre_design', 'Pre-Design'),
        ('schematic_design', 'Schematic Design'),
        ('design_development', 'Design Development'),
        ('construction_docs', 'Construction Documents'),
        ('bidding', 'Bidding'),
        ('construction', 'Construction'),
        ('post_construction', 'Post-Construction'),
    )
    STATUS_CHOICE = (
        ('pending', "Pending"),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on hold', 'On Hold')
    )
    name = models.CharField(max_length=255)
    client = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='projects')
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    phase = models.CharField(max_length=30, choices=PHASE_CHOICES, default='pre_design')
    status = models.CharField(max_length=50, choices=STATUS_CHOICE, default='pending')
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class FinancialTransaction(models.Model):
    """
    The universal Financial Transaction model, update for phase 1 requirements
    """

    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('void', 'Void'),
    )

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='transactions',
        help_text="The project this transaction is associated with."
    )
    # The 'Client Name' is derived from project.client.name

    vendor = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, # Make it optional, as it only applies to expenses
        limit_choices_to={'contact_type': 'supplier'}, # Ensures only suppliers can be chosen
        help_text="The vendor/supplier for this expense."
    )

    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="e.g., 'Bank Transfer', 'Cash', 'Credit Card'"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="The value of the transaction."
    )

    invoice_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Associated invoice number,primarily for revenue"
    )

    is_received = models.BooleanField(
        default=False,
        help_text="Toggled to True when payment is confirmed"
    )

    # This directly implements your 'Received?' toggle.
    
    transaction_date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} for {self.project.name}"
