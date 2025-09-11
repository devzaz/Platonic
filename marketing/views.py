# marketing/views.py
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.template import Template, Context
from django.views.decorators.http import require_POST

from .models import Campaign, ContentAsset, MailingList, Subscriber, EmailCampaign, SocialPost
from .forms import EmailTemplateForm, SubscriberForm, MailingListForm, EmailCampaignForm
from .services import start_email_campaign



import mimetypes
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect


from .forms import AssetForm


from datetime import datetime, timedelta
import calendar as pycal
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import EmailCampaign, SocialPost


from django.conf import settings


from decimal import Decimal
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.forms.models import model_to_dict



from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.files.uploadedfile import UploadedFile
# --- DASHBOARD ---



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
            "leads_this_month": 240,     
            "conversion_rate": "4.2%",   
            "website_traffic": "12.5k",  
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









# Api building for tools
@ensure_csrf_cookie
def marketing_tools(request):
    return render(request, 'marketing/dashboard.html')




@require_http_methods(["GET"])
def assets_list_api(request):
    """
    Return all assets as JSON for your grid.
    """
    data = []
    qs = ContentAsset.objects.filter(content_type='brand_visual').order_by("-id").only("id", "title", "asset_file")
    for a in qs:
        url = a.asset_file.url if a.asset_file else ""
        size = a.asset_file.size if a.asset_file else 0
        mt, _ = mimetypes.guess_type(url)
        data.append({
            "id": a.id,
            "title": a.title,
            "url": url,                      # direct media URL (works for previews)
            "download": f"/marketing/assets/{a.id}/download/",   # nicer download route
            "size": size,
            "mimetype": mt or "application/octet-stream",
            "filename": os.path.basename(a.asset_file.name) if a.asset_file else "",
        })
    return JsonResponse({"results": data})



@require_http_methods(["POST"])
@csrf_protect
def asset_upload_api(request):
    """
    Handle multipart/form-data from your modal form.
    Accepts: title + asset_file
    """
    form = AssetForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    asset = form.save(commit=False)
    # ensure a content_type if you need one, or leave None
    if not getattr(asset, "content_type", None):
        asset.content_type = "brand_visual"
    asset.save()

    return JsonResponse({
        "ok": True,
        "asset": {
            "id": asset.id,
            "title": asset.title,
            "url": asset.asset_file.url if asset.asset_file else "",
            "download": f"/marketing/assets/{asset.id}/download/",
        }
    }, status=201)


@require_http_methods(["POST", "DELETE"])
@csrf_protect
def asset_delete_api(request, pk: int):
    """
    Delete DB row and physical file.
    """
    asset = get_object_or_404(ContentAsset, pk=pk)
    # remove file from storage first (without saving model)
    if asset.asset_file:
        asset.asset_file.delete(save=False)
    asset.delete()
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def asset_download_view(request, pk: int):
    asset = get_object_or_404(ContentAsset, pk=pk)
    if not asset.asset_file:
        return HttpResponseBadRequest("No file attached to this asset.")
    f = asset.asset_file.open("rb")
    filename = os.path.basename(asset.asset_file.name)
    mime, _ = mimetypes.guess_type(filename)
    resp = FileResponse(f, content_type=mime or "application/octet-stream")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp



def _month_range_aware(year: int, month: int):
    """
    Returns (start, end) datetimes for the given month.
    start is inclusive (00:00:00 on the 1st), end is exclusive (00:00:00 on the 1st of next month).
    If USE_TZ=True, they are timezone-aware using the current timezone.
    """
    # naive starts
    start_naive = datetime(year, month, 1, 0, 0, 0)
    # compute first of next month
    if month == 12:
        end_naive = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        end_naive = datetime(year, month + 1, 1, 0, 0, 0)

    if settings.USE_TZ:
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(start_naive, tz)
        end = timezone.make_aware(end_naive, tz)
    else:
        start = start_naive
        end = end_naive
    return start, end


@require_GET
def calendar_items_api(request):
    """
    GET /marketing/api/calendar/?year=YYYY&month=MM
    Returns SocialPost.scheduled_time and EmailCampaign.sent_on items within that month.
    """
    try:
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        assert 1 <= month <= 12
    except Exception:
        return JsonResponse({"error": "Provide valid ?year=YYYY&month=1-12"}, status=400)

    month_start, month_end = _month_range_aware(year, month)

    # Social posts in range
    social_qs = (
        SocialPost.objects
        .select_related("social_account", "content_asset")
        .filter(scheduled_time__gte=month_start, scheduled_time__lt=month_end)
    )

    # Email campaigns in range (using sent_on; add scheduled_for later if you introduce it)
    email_qs = (
        EmailCampaign.objects
        .select_related("email_template", "mailing_list")
        .filter(sent_on__isnull=False, sent_on__gte=month_start, sent_on__lt=month_end)
    )

    items = []

    for sp in social_qs:
        items.append({
            "type": "social",
            "id": sp.id,
            "platform": sp.social_account.platform,
            "account": sp.social_account.account_name,
            "title": sp.content_asset.title,
            "status": sp.status,
            "when": timezone.localtime(sp.scheduled_time).isoformat() if settings.USE_TZ else sp.scheduled_time.isoformat(),
            "url": sp.post_url or "",
        })

    for ec in email_qs:
        # If you later add EmailCampaign.scheduled_for, prefer that when present.
        when_dt = ec.sent_on
        items.append({
            "type": "email",
            "id": ec.id,
            "subject": ec.subject,
            "template": ec.email_template.title,
            "list": ec.mailing_list.name,
            "status": ec.status,
            "when": timezone.localtime(when_dt).isoformat() if (settings.USE_TZ and when_dt) else (when_dt.isoformat() if when_dt else None),
        })

    return JsonResponse({"results": items})




@require_http_methods(["GET"])
def email_campaigns_api(request):
    """
    Returns recent email campaigns with their template name, subject, status,
    and helpful action URLs (preview, send_now).
    """
    qs = (
        EmailCampaign.objects
        .select_related("email_template", "mailing_list")
        .order_by("-id")[:200]
    )

    results = []
    for c in qs:
        results.append({
            "id": c.id,
            "template_title": c.email_template.title if c.email_template else "",
            "subject": c.subject,
            "status": c.status,  # Draft / Sending / Sent
            "mailing_list": c.mailing_list.name if c.mailing_list else "",
            "sent_on": timezone.localtime(c.sent_on).isoformat() if (settings.USE_TZ and c.sent_on) else (c.sent_on.isoformat() if c.sent_on else None),
            "preview_url": request.build_absolute_uri(reverse("marketing:campaign_preview", args=[c.id])),
            "send_now_url": request.build_absolute_uri(reverse("marketing:send_now", args=[c.id])),
        })
    return JsonResponse({"results": results})






@require_http_methods(["GET", "POST"])
@csrf_protect
def campaigns_api(request):
    """
    GET  -> list campaigns (latest first)
    POST -> create campaign (expects name, status, channel, budget)
    """
    if request.method == "GET":
        qs = Campaign.objects.order_by("-id")
        data = []
        for c in qs:
            data.append({
                "id": c.id,
                "name": c.name,
                "status": c.status,          # Planning / Active / Completed
                "channel": c.channel,
                "budget": str(c.budget),     # serialize Decimal
                # Placeholders; you can compute later if you add related models:
                "leads": None,
                "roi": None,
            })
        return JsonResponse({"results": data})

    # POST (create)
    name = request.POST.get("name", "").strip()
    status = request.POST.get("status", "Planning").strip()
    channel = request.POST.get("channel", "").strip()
    budget_raw = request.POST.get("budget", "0").strip()

    errors = {}
    if not name:
        errors["name"] = "This field is required."
    if status not in dict(Campaign.STATUS_CHOICES):
        errors["status"] = f"Invalid status. Choose one of: {', '.join(dict(Campaign.STATUS_CHOICES).keys())}"
    if not channel:
        errors["channel"] = "This field is required."

    try:
        budget = Decimal(budget_raw or "0")
        if budget < 0:
            raise ValueError
    except Exception:
        errors["budget"] = "Enter a valid non-negative number."

    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    c = Campaign.objects.create(
        name=name,
        status=status,
        channel=channel,
        budget=budget
    )
    return JsonResponse({
        "ok": True,
        "campaign": {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "channel": c.channel,
            "budget": str(c.budget),
            "leads": None,
            "roi": None,
        }
    }, status=201)


@require_http_methods(["PATCH", "DELETE"])
@csrf_protect
def campaign_detail_api(request, pk: int):
    """
    PATCH -> update any of: name, status, channel, budget
    DELETE -> delete campaign
    """
    c = get_object_or_404(Campaign, pk=pk)

    if request.method == "DELETE":
        c.delete()
        return JsonResponse({"ok": True})

    # PATCH
    # Expecting form-encoded or JSON; we’ll accept both lightly.
    data = request.POST or {}
    if request.content_type and "application/json" in request.content_type:
        import json
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            data = {}

    allowed_fields = {"name", "status", "channel", "budget"}
    updates = {}
    errors = {}

    for field in allowed_fields:
        if field in data:
            val = str(data[field]).strip()
            if field == "status":
                if val not in dict(Campaign.STATUS_CHOICES):
                    errors["status"] = f"Invalid status. Choose one of: {', '.join(dict(Campaign.STATUS_CHOICES).keys())}"
                else:
                    updates["status"] = val
            elif field == "budget":
                try:
                    bd = Decimal(val or "0")
                    if bd < 0:
                        raise ValueError
                    updates["budget"] = bd
                except Exception:
                    errors["budget"] = "Enter a valid non-negative number."
            else:
                if not val:
                    errors[field] = "This field is required."
                else:
                    updates[field] = val

    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    for k, v in updates.items():
        setattr(c, k, v)
    if updates:
        c.save(update_fields=list(updates.keys()))

    return JsonResponse({
        "ok": True,
        "campaign": {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "channel": c.channel,
            "budget": str(c.budget),
            "leads": None,
            "roi": None,
        }
    })




CONTENT_TYPE_MAP = {
    "articles": "article",
    "captions": "caption",
    "emails": "email_template",
}

def _serialize_asset(a):
    return {
        "id": a.id,
        "title": a.title,
        "content_type": a.content_type,   # 'article' | 'caption' | 'email_template'
        "body": a.body or "",
        "file_url": (a.asset_file.url if a.asset_file else ""),
        "filename": (os.path.basename(a.asset_file.name) if a.asset_file else ""),
    }

@require_http_methods(["GET", "POST"])
@csrf_protect
def content_assets_api(request):
    """
    GET  /marketing/api/content/?type=articles|captions|emails
    POST (multipart/form-data): title, content_type (article|caption|email_template), body?, asset_file?
    """
    if request.method == "GET":
        tab = (request.GET.get("type") or "").strip().lower()
        model_type = CONTENT_TYPE_MAP.get(tab)
        if not model_type:
            # default: return all, grouped (frontend may not use this, but handy)
            qs = ContentAsset.objects.all().order_by("-id")
            results = [_serialize_asset(a) for a in qs]
            return JsonResponse({"results": results})

        qs = ContentAsset.objects.filter(content_type=model_type).order_by("-id")
        return JsonResponse({"results": [_serialize_asset(a) for a in qs]})

    # POST (create)
    title = (request.POST.get("title") or "").strip()
    content_type = (request.POST.get("content_type") or "").strip()
    body = request.POST.get("body") or ""
    asset_file = request.FILES.get("asset_file")

    errors = {}
    if not title:
        errors["title"] = "This field is required."
    if content_type not in dict(ContentAsset.CONTENT_TYPES):
        errors["content_type"] = f"Choose one of: {', '.join(dict(ContentAsset.CONTENT_TYPES).keys())}"

    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    obj = ContentAsset(title=title, content_type=content_type, body=body)
    if isinstance(asset_file, UploadedFile):
        obj.asset_file = asset_file
    obj.save()

    return JsonResponse({"ok": True, "item": _serialize_asset(obj)}, status=201)


@require_http_methods(["PATCH", "DELETE"])
@csrf_protect
def content_asset_detail_api(request, pk: int):
    """
    PATCH (JSON or multipart not needed; we accept JSON): title?, body?
    DELETE
    """
    obj = get_object_or_404(ContentAsset, pk=pk)

    if request.method == "DELETE":
        if obj.asset_file:
            obj.asset_file.delete(save=False)
        obj.delete()
        return JsonResponse({"ok": True})

    # PATCH (JSON)
    data = {}
    if request.content_type and "application/json" in request.content_type:
        import json
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            data = {}

    title = data.get("title")
    body = data.get("body")

    updates = {}
    errors = {}
    if title is not None:
        title = str(title).strip()
        if not title:
            errors["title"] = "This field is required."
        else:
            updates["title"] = title
    if body is not None:
        updates["body"] = str(body)

    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    for k, v in updates.items():
        setattr(obj, k, v)
    if updates:
        obj.save(update_fields=list(updates.keys()))

    return JsonResponse({"ok": True, "item": _serialize_asset(obj)})