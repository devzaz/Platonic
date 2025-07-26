from django.db import models
from django.conf import settings
from decimal import Decimal

class Contact(models.Model):
    """
    Store Information about clients, suppliers etc.
    """

    TYPE_COICES =(
        ('client','Client'),
        ('supplier', 'Supplier'),
        ('consultant', 'Consultant')
    )

    contact_type = models.CharField(max_length=30, choices=TYPE_COICES)
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True, help_text="Optional")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_accounts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    performance_rating = models.PositiveSmallIntegerField(
        null=True, 
        blank=True, 
        help_text="Vendor rating from 1 to 5"
    )

    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Internal notes on vendor performance or reliability"
    )
    
    def __str__(self):
        return self.name
    


class Lead(models.Model):
    """
    Represents a potential sales opportunity
    """

    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal_sent', 'Proposal Sent'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )

    Contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=100, blank=True, help_text="e.g., 'Website', 'Referral'")
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    assign_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads"
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" Lead for {self.Contact.name}"
    

class Quotation(models.Model):
    """
    A formal offer/quotation sent to a client for a lead.
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'), # This is the "Won" status
        ('rejected', 'Rejected'),
    )
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='quotations')
    quotation_id = models.CharField(max_length=50, unique=True, help_text="e.g., Q-2025-001")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issue_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='created_quotations'
    )
    details = models.TextField(blank=True, null=True)

    def total_amount(self):
        """Calculates the total amount from all its items as Decimal"""
        return sum((Decimal(item.total) for item in self.items.all()), Decimal('0.00'))

    def __str__(self):
        return self.quotation_id
    



class QuotationItem(models.Model):
    """
    Represents a single line item within a Quotation.
    This is the "linked model".
    """
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='items' # This link allows us to do quotation.items.all()
    )
    description = models.CharField(max_length=255, help_text="e.g., 'Phase 1: Concept Design'")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total(self):
        """Calculates the line item's total price."""
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"Item for Quotaion {self.quotation.quotation_id}: {self.description}"

