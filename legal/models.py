# legal/models.py
from django.db import models
from projects.models import Project

class ContractTemplate(models.Model):
    """Stores contract templates with placeholders."""
    name = models.CharField(max_length=255)
    template_type = models.CharField(
        max_length=50,
        choices=(('client_contract', 'Client Contract'), ('employment_nda', 'Employment NDA')),
        help_text="The type of contract this template is for."
    )
    content = models.TextField(
        help_text="The full text of the contract. Use placeholders like {{client_name}} or {{project_budget}}."
    )

    def __str__(self):
        return self.name

class Contract(models.Model):
    """An instance of a generated contract."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contracts')
    template_used = models.ForeignKey(ContractTemplate, on_delete=models.PROTECT)
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Zoho Sign Integration Fields
    zoho_request_id = models.CharField(max_length=100, blank=True, null=True)
    zoho_sign_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=(('draft', 'Draft'), ('sent_for_signature', 'Sent'), ('signed', 'Signed')),
        default='draft'
    )

    def __str__(self):
        return f"Contract for {self.project.name} based on {self.template_used.name}"