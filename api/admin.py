from django.contrib import admin
from .models import ContactUs, Career


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone", "message")
    list_filter = ("created_at",)


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "position", "created_at")
    search_fields = ("full_name", "email", "phone", "position")
    list_filter = ("position", "created_at")