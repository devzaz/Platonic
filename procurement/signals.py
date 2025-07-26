from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VendorInvoice
from projects.models import FinancialTransaction
from core.models import ChartOfAccounts



@receiver(post_save, sender=VendorInvoice)
def create_payable_on_invoice_approval(sender, instance, created,**kwargs):
    """
    When a VendorInvoice status is changed to 'approved_for_payment',
    automatically create a liability transaction (Accounts Payable).
    """
    if not created and instance.status == 'approved_for_payment':
        try:
            # Find the 'Accounts Payable' account from your CoA.
            # IMPORTANT: Your CoA CSV must have a predictable code for this.
            accounts_payable_account = ChartOfAccounts.objects.get(code='2010') 

            # Check if a transaction for this invoice already exists
            if not FinancialTransaction.objects.filter(invoice_number=instance.invoice_id).exists():
                FinancialTransaction.objects.create(
                    project = instance.purchase_order.project,
                    account = accounts_payable_account,
                    amount = instance.total_amount,
                    # For liabilities, a credit increases the balance.
                    is_debit = False,
                    transaction_date = instance.invoice_date,
                    description = f"Accounts payable for invoice {instance.invoice_id} from {instance.vendor.name}",
                    invoice_number = instance.invoice_id,
                    vendor = instance.vendor,
                    status = 'approved',

                )
                print(f"Created Accounts Payable transaction for invoice {instance.invoice_id}")
        except ChartOfAccounts.DoesNotExist:
            print("ERROR: 'Accounts Payable' account not found in Chart of Accounts.")