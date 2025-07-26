from django.urls import path
from .views import *


urlpatterns = [
    path('operations_home/', index, name='operations_index'),
]
