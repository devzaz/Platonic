from django.urls import path
from .views import *


urlpatterns = [
    path('sales_dashboard/', dashboard, name='SalesDashboard'),
    path('add_lead/', add_lead_view, name='add_lead'),
]
