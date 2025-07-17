from django.urls import path
from .views import *


urlpatterns = [
    path('sales_dashboard/', dashboard, name='SalesDashboard')
]
