from django.urls import path
from .views import *


urlpatterns = [
    path('sales_dashboard/', dashboard, name='SalesDashboard'),
    path('add_lead/', add_lead_view, name='add_lead'),
    path('add_contact/', add_contact_view, name='add_contact'),
    path('api/contacts/', get_contacts_data, name='api_get_contacts'),
    path('delete_contact/<str:email>/', delete_contact, name='delete_contact'),
    path('api/leads/', get_leads_data, name='api_get_leads'),


    path("api/quotations/", quotation_create, name="quotation_create"),                 # POST
    path("api/quotations/<int:pk>/", quotation_detail, name="quotation_detail"),       # GET, PATCH, DELETE
    path("api/quotations/<int:pk>/items/", item_create, name="quotation_item_create"), # POST
    path("api/quotations/<int:qpk>/items/<int:ipk>/", item_detail, name="quotation_item_detail"),  # PATCH, DELETE

    path("api/leads/won/", won_leads, name="won_leads"),   

]
