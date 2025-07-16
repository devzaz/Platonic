from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model to include roles for Role-Based Access Control (RBAC).
    """
    ROLE_CHOICES = (
        ('ceo', 'CEO'),
        ('accountant', 'Accountant'),
        ('project_manager', 'Project Manager'),
        ('engineer', 'Engineer'),
        ('sales', 'Sales'),
        ('client', 'Client'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return self.username


class ChartOfAccounts(models.Model):
    """
    Represents the Chart of Accounts (CoA)
    It's the hierarchial to supprot multi-level accounting.
    """

    ACCOUNT_CATEGORY_CHOICES = (
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('REVENUE', 'Revenue'),
        ('COGS', 'Cost of Goods Sold'),
        ('EXPENSE', 'Expense'),
    )

    name = models.CharField(max_length=225)
    code = models.CharField(max_length=20, unique=True, help_text="The unique account number/code")
    category = models.CharField(max_length=10, choices=ACCOUNT_CATEGORY_CHOICES )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent account for creating a hierarchy"
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)


    class Meta:
        verbose_name = "Chart of Account"
        verbose_name_plural = "Chart of Accounts"
        ordering = ['code']

    
    def __str__(self):
        return f"{self.code}- {self.name}"
    
    