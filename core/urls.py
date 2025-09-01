from django.urls import path
from .views import login_page, index, all_departments, executive_dashboard, administration
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', all_departments, name='all_dep'),
    path('home', index, name='home'),
    path('accounts/login/', login_page, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('executive-dashboard/', executive_dashboard, name='executive'),
    path('administration/', administration, name='administration'),  
]
