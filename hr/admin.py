from django.contrib import admin
from .models import *


admin.site.register(Employee)
admin.site.register(LeaveRequest)
admin.site.register(Timesheet)
admin.site.register(Payroll)
admin.site.register(Payslip)
