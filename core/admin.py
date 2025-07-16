from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ChartOfAccounts

class CustomUserAdmin(UserAdmin):
    # Add 'role' to the display and fieldsets
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )



class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category','parent', 'is_active')
    list_filter = ('category', 'is_active', 'parent')
    search_fields = ('name', 'code')
    list_per_page = 25





admin.site.register(User, CustomUserAdmin)
admin.site.register(ChartOfAccounts, ChartOfAccountsAdmin)