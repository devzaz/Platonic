# marketing/urls.py
from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    path('tools/', views.others, name='tools'),

    # Email Templates (ContentAsset with content_type='email_template')
    path("email-templates/", views.email_template_list, name="email_template_list"),
    path("email-templates/new/", views.email_template_create, name="email_template_create"),
    path("email-templates/<int:pk>/edit/", views.email_template_edit, name="email_template_edit"),

    # Subscribers & Mailing Lists (simple)
    path("subscribers/", views.subscriber_list, name="subscriber_list"),
    path("subscribers/new/", views.subscriber_create, name="subscriber_create"),
    path("mailing-lists/", views.mailing_list_list, name="mailing_list_list"),
    path("mailing-lists/new/", views.mailing_list_create, name="mailing_list_create"),

    # Campaigns
    path("campaigns/", views.email_campaign_list, name="email_campaign_list"),
    path("campaigns/new/", views.email_campaign_create, name="email_campaign_create"),
    path("campaigns/<int:pk>/preview/", views.campaign_preview, name="campaign_preview"),
    path("campaigns/<int:pk>/send/", views.send_now_view, name="send_now"),
]
