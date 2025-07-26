from django.db import models
from django.conf import settings
from projects.models import Project # For timesheets
from projects.models import FinancialTransaction
from core.models import ChartOfAccounts
import datetime

class Employee(models.Model):
    """Detailed employee profile, linked to a system user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    joining_date = models.DateField()
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    bank_account_number = models.CharField(max_length=50, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class LeaveRequest(models.Model):
    """Model for employees to request leave."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Leave for {self.employee} from {self.start_date}"

class Timesheet(models.Model):
    """For logging hours against projects."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='timesheets')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField(help_text="Description of work performed.")

    def __str__(self):
        return f"{self.hours_worked} hours by {self.employee} on {self.date}"

class Payroll(models.Model):
    """Represents a payroll run for a specific period."""
    period_month = models.PositiveSmallIntegerField()
    period_year = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=20,
        choices=(('draft', 'Draft'), ('finalized', 'Finalized'), ('posted', 'Posted to Ledger')),
        default='draft'
    )

    def __str__(self):
        return f"Payroll for {self.period_month}/{self.period_year}"
    
    def post_to_ledger(self):
        """Posts the total payroll expense to the financial ledger."""
        if self.status != 'finalized':
            raise ValueError("Payroll must be finalized before posting to ledger.")
        
        try:
            salary_expense_account = ChartOfAccounts.objects.get(code='6010')
            cash_account = ChartOfAccounts.objects.get(code='1010') # Example cash/bank code

            total_payroll_cost = sum(p.net_pay for p in self.payslips.all())


            if total_payroll_cost > 0:
                # 1. Debit the Salary Expense account
                FinancialTransaction.objects.create(
                    account=salary_expense_account,
                    amount=total_payroll_cost,
                    is_debit=True,
                    transaction_date=datetime.date.today(), # Or end of period
                    description=f"Total salary expense for {self.period_month}/{self.period_year}",
                    status='approved'
                )
                # 2. Credit the Cash/Bank account
                FinancialTransaction.objects.create(
                    account=cash_account,
                    amount=total_payroll_cost,
                    is_debit=False,
                    transaction_date=datetime.date.today(), # Or end of period
                    description=f"Salary payment for {self.period_month}/{self.period_year}",
                    status='approved'
                )
                 
                self.status = 'posted'
                self.save()
                return True
        
        except ChartOfAccounts.DoesNotExist:
            print("ERROR: Salary or Cash accounts not found in CoA.")
            return False


class Payslip(models.Model):
    """An individual employee's payslip for a payroll run."""
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Payslip for {self.employee} - {self.payroll}"