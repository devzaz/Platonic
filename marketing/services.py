from django.template import Template, Context
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .models import EmailCampaign

def start_email_campaign(campaign_id: int) -> str:
    try:
        campaign = EmailCampaign.objects.select_related("email_template", "mailing_list").get(id=campaign_id)
    except EmailCampaign.DoesNotExist:
        return "Campaign not found."

    subscribers = campaign.mailing_list.subscribers.all()
    template_html = campaign.email_template.body or ""
    template = Template(template_html)

    emails_sent = 0
    for sub in subscribers:
        context = Context({"first_name": sub.first_name, "email": sub.email})
        html_message = template.render(context)
        text_message = strip_tags(html_message) or " "

        msg = EmailMultiAlternatives(
            subject=campaign.subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
        )
        msg.attach_alternative(html_message, "text/html")
        try:
            msg.send(fail_silently=False)
            emails_sent += 1
        except Exception as e:
            print(f"Failed to send to {sub.email}: {e}")

    campaign.status = "Sent"
    campaign.sent_on = timezone.now()
    campaign.save(update_fields=["status", "sent_on"])
    return f"Campaign '{campaign.subject}' sent to {emails_sent} subscribers."

# def publish_social_post(post_id):
#     """
#     Connects to a social media platform's API and publishes the post.
#     This should be run as a background task.
#     """
#     try:
#         post = SocialPost.objects.get(id=post_id, status='Scheduled')
#     except SocialPost.DoesNotExist:
#         return "Post not found or not in scheduled state."

#     print(f"Attempting to publish post {post.id} to {post.social_account.platform}...")
    
#     # --- THIS IS WHERE PLATFORM-SPECIFIC API LOGIC GOES ---
#     # Each platform (Facebook, LinkedIn, etc.) has a different, complex API.
#     # You would need to write an API client for each one.
    
#     # Example pseudocode for a LinkedIn API client:
#     if post.social_account.platform == 'LinkedIn':
#         # api_client = LinkedInClient(api_key=post.social_account.api_key)
#         # success, post_url = api_client.create_post(text=post.content_asset.body)
#         success = True # Placeholder
#         post_url = f"https://linkedin.com/feed/update/{int(time.time())}" # Placeholder
#     else:
#         # Handle other platforms
#         success = False

#     if success:
#         post.status = 'Published'
#         post.post_url = post_url
#         post.save()
#         return f"Post published successfully to {post.social_account.platform}."
#     else:
#         post.status = 'Failed'
#         post.save()
#         return "Failed to publish post."