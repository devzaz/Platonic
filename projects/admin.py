from django.contrib import admin
from .models import Project,FinancialTransaction


admin.site.register(Project)
admin.site.register(FinancialTransaction)