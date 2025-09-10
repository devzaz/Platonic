# marketing/models.py
from django.db import models
from django.conf import settings

# M1: Campaign Planning & Tracking (No changes needed)
class Campaign(models.Model):
    STATUS_CHOICES = (('Planning', 'Planning'), ('Active', 'Active'), ('Completed', 'Completed'))
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planning')
    channel = models.CharField(max_length=100, help_text="e.g., Social Media, Email, Print")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # ... other fields

    def __str__(self):
        return self.name

# M2 & M10: Content & Asset Library (No changes needed)
class ContentAsset(models.Model):
    CONTENT_TYPES = (
        ('article', 'Blog Article'), 
        ('caption', 'Social Media Caption'),
        ('email_template', 'Email Template'), # Crucial for our email system
        ('brand_visual', 'Brand Visual'),
        # ... other types
    )
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    body = models.TextField(blank=True, help_text="For text-based content like articles or HTML emails.")
    asset_file = models.FileField(upload_to='marketing_assets/', null=True, blank=True)
    # ... other fields

    def __str__(self):
        return self.title

# --- NEW MODELS FOR IN-HOUSE EMAIL MARKETING (M6) ---
class MailingList(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    

    def __str__(self):
        return self.name

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    subscribed_on = models.DateTimeField(auto_now_add=True)
    mailing_lists = models.ManyToManyField(MailingList, related_name='subscribers')

    def __str__(self):
        return self.email

class EmailCampaign(models.Model):
    STATUS_CHOICES = (('Draft', 'Draft'), ('Sending', 'Sending'), ('Sent', 'Sent'))
    subject = models.CharField(max_length=255)
    email_template = models.ForeignKey(ContentAsset, on_delete=models.PROTECT, limit_choices_to={'content_type': 'email_template'})
    mailing_list = models.ForeignKey(MailingList, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    sent_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject

# --- REVISED MODELS FOR IN-HOUSE SOCIAL MEDIA POSTING (M3) ---
class SocialAccount(models.Model):
    """Securely stores credentials for connecting to social platforms."""
    PLATFORM_CHOICES = (('LinkedIn', 'LinkedIn'), ('Instagram', 'Instagram'), ('Facebook', 'Facebook'))
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_name = models.CharField(max_length=255)
    # In a real app, you'd use a secure way to store encrypted API tokens (OAuth2)
    api_key = models.CharField(max_length=255, help_text="Store securely!") 

    def __str__(self):
        return f"{self.account_name} ({self.platform})"

class SocialPost(models.Model):
    """The scheduled post, now linked to our own SocialAccount."""
    STATUS_CHOICES = (('Draft', 'Draft'), ('Scheduled', 'Scheduled'), ('Published', 'Published'), ('Failed', 'Failed'))
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    content_asset = models.ForeignKey(ContentAsset, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    post_url = models.URLField(blank=True, null=True, help_text="URL of the live post after publishing.")

# ... (MarketingEvent model remains the same) ...