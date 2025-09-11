# marketing/urls.py
from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    path('tools/', views.marketing_tools, name='tools'),

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


    # JSON API
    path("api/assets/", views.assets_list_api, name="assets_list_api"),
    path("api/assets/upload/", views.asset_upload_api, name="asset_upload_api"),
    path("api/assets/<int:pk>/delete/", views.asset_delete_api, name="asset_delete_api"),
    # Download (streams file with original filename)
    path("assets/<int:pk>/download/", views.asset_download_view, name="asset_download_view"),

    # NEW: calendar API
    path("api/calendar/", views.calendar_items_api, name="calendar_items_api"),


    # JSON for Email Marketing table
    path("api/email/campaigns/", views.email_campaigns_api, name="email_campaigns_api"),

    # Campaigns API
    path("api/campaigns/", views.campaigns_api, name="campaigns_api"),              # GET list, POST create
    path("api/campaigns/<int:pk>/", views.campaign_detail_api, name="campaign_detail_api"),  # PATCH/DELETE (optional)


    # Content CMS API
    path("api/content/", views.content_assets_api, name="content_assets_api"),              # GET list (by type), POST create
    path("api/content/<int:pk>/", views.content_asset_detail_api, name="content_asset_detail_api"),  # PATCH/DELETE

    
]
