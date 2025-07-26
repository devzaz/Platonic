from django.urls import path
from . import views


urlpatterns = [
    path('hr_home/', views.index, name='hr_home')
]
