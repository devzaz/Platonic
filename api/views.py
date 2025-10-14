from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


from .models import ContactUs, Career, Category, Project, ProjectImage, ProjectVideo
from .serializers import ContactUsSerializer, CareerSerializer, ProjectSerializer, ProjectImageSerializer, CategorySerializer, ProjectVideoSerializer
from .permissions import IsCreateOrStaffRead


class ContactUsViewSet(viewsets.ModelViewSet):
    queryset = ContactUs.objects.all().order_by('-created_at')
    serializer_class = ContactUsSerializer
    permission_classes = [IsCreateOrStaffRead]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["created_at"]
    search_fields = ["name", "email", "phone", "message"]
    ordering_fields = ["created_at", "name"]


class CareerViewSet(viewsets.ModelViewSet):
    queryset = Career.objects.all().order_by('-created_at')
    serializer_class = CareerSerializer
    permission_classes = [IsCreateOrStaffRead]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["position", "created_at"]
    search_fields = ["full_name", "email", "phone", "position", "cover_letter"]
    ordering_fields = ["created_at", "full_name"]


    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def stats(self, request):
        # Simple admin‑only summary by position
        from django.db.models import Count
        data = (
        Career.objects.values("position")
        .annotate(total=Count("id"))
        .order_by("position")
        )
        return Response(list(data))
    


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'status', 'year']


class ProjectImageViewSet(viewsets.ModelViewSet):
    queryset = ProjectImage.objects.all()
    serializer_class = ProjectImageSerializer



class ProjectVideoViewSet(viewsets.ModelViewSet):
    queryset = ProjectVideo.objects.all()
    serializer_class = ProjectVideoSerializer