from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactUsViewSet, CareerViewSet, CategoryViewSet, ProjectImageViewSet, ProjectViewSet, ProjectVideoViewSet


router = DefaultRouter()
router.register(r"contact", ContactUsViewSet, basename="contact")
router.register(r"careers", CareerViewSet, basename="careers")
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"project-images", ProjectImageViewSet, basename="project-images")
router.register(r"project-videos", ProjectVideoViewSet, basename="project-videos")


urlpatterns = [
    path("", include(router.urls)),
]