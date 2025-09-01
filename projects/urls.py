from django.urls import path
from . import views


urlpatterns = [
    path('api/projects/', views.project_api, name='project_api'),
    path('api/cashflow/', views.cashflow_api, name='cashflow_api'),
    path('api/revenue-profit/', views.revenue_profit_api, name='revprof_api'),
    path('api/project-profitability/', views.project_profitability_api, name='project_profitability_api'),
    path('api/kpis/', views.kpis_api, name='kpis_api'),
]
