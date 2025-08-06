from django.urls import path
from .views import login_page, index
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', index, name='home'),
    path('accounts/login/', login_page, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
