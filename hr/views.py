from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *



@login_required
def index(request):
    return render(request, 'hr/index.html')



def employee_list_api(request):
    employees = list(
        Employee.objects.filter(is_active=True).select_related('user')
        .values(
            "user__username", "employee_id","department","designation"
        )
    )
    return JsonResponse({"employees": employees})



def leave_requests_api(request):
    leave_requests = list(
        LeaveRequest.objects.filter(status='pending')
        .values(
            "employee__user__username", "start_date", "end_date", "reason", "status"
        )
    )
    return JsonResponse({"leave_requests": leave_requests})


def payslip_list_api(request):
    payslips = list(
        Payslip.objects.all().select_related('payroll')
        .values(
            "employee__user__username", "basic_salary", "net_pay", "payroll__period_month", "payroll__period_year","payroll__status" 
        )
    )

    return JsonResponse({"payslips": payslips})
