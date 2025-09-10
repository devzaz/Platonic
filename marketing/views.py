# marketing/views.py
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.template import Template, Context
from django.views.decorators.http import require_POST

from .models import Campaign, ContentAsset, MailingList, Subscriber, EmailCampaign, SocialPost
from .forms import EmailTemplateForm, SubscriberForm, MailingListForm, EmailCampaignForm
from .services import start_email_campaign

# --- DASHBOARD ---

def others(request):
    return render(request, 'marketing/dashboard.html')

def dashboard(request):
    base_campaigns = Campaign.objects.all()

    # Do all filtering/aggregations on the unsliced queryset
    active_campaigns = base_campaigns.filter(status="Active").count()

    # Slice only when you’re done filtering
    campaigns = base_campaigns[:10]

    # These are fine (we don't filter them later)
    email_templates = ContentAsset.objects.filter(content_type="email_template")[:50]
    social_posts = SocialPost.objects.order_by("scheduled_time")[:10]

    context = {
        "campaigns": campaigns,
        "email_templates": email_templates,
        "social_posts": social_posts,
        "metrics": {
            "active_campaigns": active_campaigns,
            "leads_this_month": 240,     # your placeholder metric
            "conversion_rate": "4.2%",   # your placeholder metric
            "website_traffic": "12.5k",  # your placeholder metric
        },
    }
    return render(request, "marketing/index.html", context)

# --- EMAIL TEMPLATES CRUD ---
def email_template_list(request):
    templates = ContentAsset.objects.filter(content_type="email_template")
    return render(request, "marketing/form_page.html", {
        "title": "Email Templates",
        "list_items": templates,
        "columns": ["Title"],
        "rows": [[t.title, reverse("marketing:email_template_edit", args=[t.id]) ] for t in templates],
        "create_url": reverse("marketing:email_template_create"),
        "create_label": "New Email Template",
        "mode": "list",
    })

def email_template_create(request):
    if request.method == "POST":
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("marketing:email_template_list")
    else:
        form = EmailTemplateForm()
    return render(request, "marketing/form_page.html", {
        "title": "Create Email Template",
        "form": form,
        "mode": "form",
    })

def email_template_edit(request, pk: int):
    obj = get_object_or_404(ContentAsset, pk=pk, content_type="email_template")
    if request.method == "POST":
        form = EmailTemplateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("marketing:email_template_list")
    else:
        form = EmailTemplateForm(instance=obj)
    return render(request, "marketing/form_page.html", {
        "title": f"Edit Email Template: {obj.title}",
        "form": form,
        "mode": "form",
    })

# --- SUBSCRIBERS / MAILING LISTS ---
def subscriber_list(request):
    items = Subscriber.objects.all()
    return render(request, "marketing/form_page.html", {
        "title": "Subscribers",
        "list_items": items,
        "columns": ["Email", "First Name"],
        "rows": [[s.email, s.first_name] for s in items],
        "create_url": reverse("marketing:subscriber_create"),
        "create_label": "Add Subscriber",
        "mode": "list",
    })

def subscriber_create(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("marketing:subscriber_list")
    else:
        form = SubscriberForm()
    return render(request, "marketing/form_page.html", {
        "title": "Add Subscriber",
        "form": form,
        "mode": "form",
    })

def mailing_list_list(request):
    items = MailingList.objects.all()
    return render(request, "marketing/form_page.html", {
        "title": "Mailing Lists",
        "list_items": items,
        "columns": ["Name", "Description"],
        "rows": [[m.name, m.description] for m in items],
        "create_url": reverse("marketing:mailing_list_create"),
        "create_label": "New Mailing List",
        "mode": "list",
    })

def mailing_list_create(request):
    if request.method == "POST":
        form = MailingListForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("marketing:mailing_list_list")
    else:
        form = MailingListForm()
    return render(request, "marketing/form_page.html", {
        "title": "New Mailing List",
        "form": form,
        "mode": "form",
    })

# --- EMAIL CAMPAIGNS ---
def email_campaign_list(request):
    items = EmailCampaign.objects.select_related("mailing_list", "email_template").all()
    return render(request, "marketing/form_page.html", {
        "title": "Email Campaigns",
        "list_items": items,
        "columns": ["Subject", "Mailing List", "Status"],
        "rows": [[c.subject, c.mailing_list.name, c.status, reverse("marketing:campaign_preview", args=[c.id]), reverse("marketing:send_now", args=[c.id])] for c in items],
        "create_url": reverse("marketing:email_campaign_create"),
        "create_label": "New Campaign",
        "mode": "campaign_list",
    })

def email_campaign_create(request):
    if request.method == "POST":
        form = EmailCampaignForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("marketing:email_campaign_list")
    else:
        form = EmailCampaignForm()
    return render(request, "marketing/form_page.html", {
        "title": "New Email Campaign",
        "form": form,
        "mode": "form",
    })

def campaign_preview(request, pk: int):
    campaign = get_object_or_404(EmailCampaign.objects.select_related("email_template", "mailing_list"), id=pk)
    template = Template(campaign.email_template.body or "")
    sub = campaign.mailing_list.subscribers.first()
    ctx = Context({
        "first_name": (sub.first_name if sub else "Friend"),
        "email": (sub.email if sub else "friend@example.com"),
    })
    html = template.render(ctx)
    return render(request, "marketing/preview.html", {"html": html, "campaign": campaign})

def send_now_view(request, pk: int):
    campaign = get_object_or_404(EmailCampaign, id=pk)
    if campaign.status == "Sent":
        return HttpResponse("Already sent.")
    campaign.status = "Sending"
    campaign.save(update_fields=["status"])
    start_email_campaign(campaign.id)
    return redirect("marketing:email_campaign_list")

