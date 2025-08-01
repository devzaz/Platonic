from django.urls import path
from .views import *


urlpatterns = [
    path('sales_dashboard/', dashboard, name='SalesDashboard'),
    path('add_lead/', add_lead_view, name='add_lead'),
    path('add_contact/', add_contact_view, name='add_contact'),
    path('api/contacts/', get_contacts_data, name='api_get_contacts'),
]
