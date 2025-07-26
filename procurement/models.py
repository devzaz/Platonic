from django.db import models
from django.conf import settings
from projects.models import Project
from sales.models import Contact # For Vendors


class PurchaseOrder(models.Model):
    """Represents a Purchase Order sent to a vendor."""
    STATUS_CHOICES = (
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ordered', 'Ordered'),
        ('partially_received', 'Partially Received'),
        ('fully_received', 'Fully Received'),
    )
    po_id = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='purchase_orders')
    vendor = models.ForeignKey(
        Contact, 
        on_delete=models.PROTECT, 
        limit_choices_to={'contact_type': 'supplier'}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_approval')
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.po_id} for {self.project.name}"
    



class PurchaseOrderItem(models.Model):
    """A single line item within a Purchase Order."""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=20, default='pcs')

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.description
    

class GoodsReceivedNote(models.Model):
    """A GRN to confirm receipt of goods against a PO."""
    grn_id = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='grns')
    received_date = models.DateField()
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.grn_id} for PO {self.purchase_order.po_id}"
    


# This is a new app, so we'll also create the Inventory model here.
class StockItem(models.Model):
    """Represents an item in inventory/stock."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    quantity_on_hand = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, default='pcs')
    warehouse_location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    





class VendorInvoice(models.Model):
    """Represents an invoice received from a vendor."""
    STATUS_CHOICES = (
        ('pending_approval', 'Pending Approval'),
        ('approved_for_payment', 'Approved for Payment'),
        ('paid', 'Paid'),
    )
    invoice_id = models.CharField(max_length=100)
    vendor = models.ForeignKey(Contact, on_delete=models.PROTECT, limit_choices_to={'contact_type': 'supplier'})
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='vendor_invoices')
    invoice_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_approval')

    def __str__(self):
        return f"Invoice {self.invoice_id} from {self.vendor.name}"
