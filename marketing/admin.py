# marketing/admin.py
from django.contrib import admin
from .models import Campaign, ContentAsset, MailingList, Subscriber, EmailCampaign, SocialAccount, SocialPost
from .services import start_email_campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "channel", "budget")
    search_fields = ("name", "channel")

@admin.register(ContentAsset)
class ContentAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "content_type")
    list_filter = ("content_type",)
    search_fields = ("title",)

@admin.register(MailingList)
class MailingListAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "subscribed_on")
    search_fields = ("email", "first_name")
    filter_horizontal = ("mailing_lists",)

@admin.action(description="Send selected email campaigns now")
def send_selected_campaigns(modeladmin, request, queryset):
    sent = 0
    for campaign in queryset:
        # Only send if not already sent
        if campaign.status != "Sent":
            campaign.status = "Sending"
            campaign.save(update_fields=["status"])
            msg = start_email_campaign(campaign.id)
            modeladmin.message_user(request, msg)
            sent += 1
    if sent == 0:
        modeladmin.message_user(request, "No campaigns were sent (already Sent?).")

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ("subject", "mailing_list", "status", "sent_on")
    list_filter = ("status", "mailing_list")
    search_fields = ("subject",)
    actions = [send_selected_campaigns]

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("account_name", "platform")

@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ("social_account", "content_asset", "scheduled_time", "status")
    list_filter = ("status", "social_account")
