from django.urls import path
from .views import index

urlpatterns = [
    path('procurement_home/', index, name='procurement_home')
]
