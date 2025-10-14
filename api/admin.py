from django.contrib import admin
from .models import ContactUs, Career, Category, Project, ProjectImage, ProjectVideo
from django.utils.html import format_html



class ProjectVideoInline(admin.TabularInline):
    model = ProjectVideo
    extra = 1
    fields = ['video', 'preview']
    readonly_fields = ['preview']


    def preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="200" controls>'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>', obj.video.url
            )
        return ""





class ProjectImageInline(admin.TabularInline):  # or StackedInline
    model = ProjectImage
    extra = 1
    fields = ['image', 'preview']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius:4px;">', obj.image.url)
        return ""

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "year", "created_at")
    search_fields = ("title", "description", "category__name", "status", "year")
    list_filter = ("category", "status", "year", "created_at")
    inlines = [ProjectImageInline, ProjectVideoInline]
    
admin.site.register(ProjectImage)
admin.site.register(ProjectVideo)
    


