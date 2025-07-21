from django.contrib import admin
from .models import *


admin.site.register(ProjectMilestone)
admin.site.register(RequestForInformation)
admin.site.register(VariationOrder)
admin.site.register(InspectionRequest)
admin.site.register(MaterialRequest)