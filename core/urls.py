from django.urls import path
from .views import login_page
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', login_page, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
