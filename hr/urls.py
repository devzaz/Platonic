from django.urls import path
from . import views


urlpatterns = [
    path('hr_home/', views.index, name='hr_home'),
    path('api/employees/', views.employee_list_api, name='employee_list_api'),
    path('api/leave_requests/', views.leave_requests_api, name='leave_requests_api'),
    path('api/payslips/', views.payslip_list_api, name='payslip_list_api'),
]
