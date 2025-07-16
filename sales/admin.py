from django.contrib import admin
from .models import Contact, Lead, Quotation, QuotationItem


admin.site.register(Contact)
admin.site.register(Lead)
admin.site.register(Quotation)
admin.site.register(QuotationItem)

