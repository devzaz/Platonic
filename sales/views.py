from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LeadForm, ContactForm
from .models import Lead, Contact
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import ProtectedError


# for handling JSON and Decimal serialization
import json
from decimal import Decimal
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from .models import Quotation, QuotationItem, Lead




@login_required(login_url='login')
def dashboard(request):
    leads = Lead.objects.all()
    contacts= Contact.objects.all()

    # Convert the QuerySet into a list of dictionaries
    

    lead_form = LeadForm()
    contact_form = ContactForm()
    context = {
        'lead_form': lead_form,
        'contact_form': contact_form
    }
    return render(request, 'sales/dashboard.html', context)


def add_lead_view(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SalesDashboard')
    else:
        form = LeadForm()
    
    context = {
        'lead_form': form,
        }
    
    return redirect('SalesDashboard')

@login_required
def add_contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            return redirect('SalesDashboard')
    else:
        form = ContactForm()
    
    context = {
        'contact_form': form,
        }
    
    return redirect('SalesDashboard')


@login_required
def get_contacts_data(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    contacts = Contact.objects.all()


    contacts_list = list(contacts.values(
        'name', 'contact_type' ,'company_name', 'phone', 'email'
    ))

    return JsonResponse({'contacts': contacts_list})


@login_required
def get_leads_data(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    
    leads = Lead.objects.all()

    leads_list = list(leads.values(
        'Contact__name', 'status', 'estimated_value', 'assign_to__username'))
    
    return JsonResponse({'leads': leads_list})


# @login_required
# def delete_contact(request, email):
#         try: 
#             contact = Contact.objects.get(email=email)
#             contact.delete()
#             messages.success(request, 'Contact deleted successfully.')
            
#         except Contact.DoesNotExist:
#             messages.error(request, 'Contact not found.')

#         return redirect('SalesDashboard')


@login_required
def delete_contact(request, email):

    contact = get_object_or_404(Contact, email=email)

    try:
        # Try to delete the object
        contact.delete()
        
        # If successful, add a success message
        messages.success(request, f"'{contact.name}' was deleted successfully.")

    except ProtectedError:
        # If it fails due to protection, add an error message
        messages.error(request, f"Cannot delete '{contact.name}' because it is being used by other items.")

    return redirect('SalesDashboard')



def nex_quotation_id():
    year = timezone.now().year
    prefix =f"Q-{year}-"
    last = Quotation.objects.filter(quotation_id__startswith=prefix).order_by('-id').first()
    n = 1
    if last:
        try:
            n  = int(last.quotation_id.split('-')[-1]) + 1
        except Exception:
            n = last.id + 1
    
    return f"{prefix}{n:03d}"


def q_to_dict(q: Quotation):
    return {
        'id': q.id,
        'quotation_id': q.quotation_id,
        'lead_id': q.lead.id,
        'lead_contact_name': q.lead.Contact.name,
        'status': q.status,
        'issue_date': q.issue_date.isoformat(),
        'created_by': q.created_by.username if q.created_by else None,
        'details': q.details,
        'total_amount': str(q.total_amount()),
        'items': [item_to_dict(i) for i in q.items.all().order_by('-id')]
        
    }
        
def item_to_dict(i: QuotationItem):
    return {
        'id': i.id,
        'title': i.title or "",
        'item_id': i.item_id,
        'description': i.description,
        'quantity': str(i.quantity),
        'unit_price': str(i.unit_price),
        'total': str(i.total)
    }


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def quotation_create(request):
    data = json.loads(request.body.decode('utf-8'))
    lead_id = data.get('lead_id')
    if not lead_id:
        return HttpResponseBadRequest("Missing lead_id")
    issue_date = data.get("issue_date") or timezone.now().date().isoformat()
    status = data.get("status") or "draft"
    details = data.get("details") or ""

    quotation = Quotation.objects.create(
        lead_id=lead_id,
        issue_date=issue_date,
        status=status,
        details=details,
        created_by=request.user,
        quotation_id=nex_quotation_id()
    )


    for it in data.get("items", []):
        QuotationItem.objects.create(
            quotation = quotation,
            title = it.get("title", ""),
            description = it.get("description", ""),
            quantity = Decimal(str(it.get("quantity", "1"))),
            unit_price = Decimal(str(it.get("unit_price", 0)))

        )
        return JsonResponse(q_to_dict(quotation), status=201)


@login_required
@require_http_methods(["GET", "PATCH", "DELETE"])
@transaction.atomic
def quotation_detail(request, pk):
    try:
        q = Quotation.objects.get(pk=pk)
    except Quotation.DoesNotExist:
        return JsonResponse({'error': 'Quotation not found'}, status=404)
    

    #optional: check if request.user has permission to access this quotation only super user can
    if request.method in ["PATCH", "DELETE"] and q.created_by != request.user.id and not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to modify this quotation.")

    if request.method == "GET":
        data = json.loads(request.body.decode('utf-8'))
        for field in ["status","details"]:
            if field in data:
                setattr(q,field,data[field])
        if "lead_id" in data:
            q.lead_id = data["lead_id"]
        if "issue_date" in data:
            q.issue_date = data["issue_date"]
        q.save()
        return JsonResponse(q_to_dict(q))
    
    #Delete
    q.delete()
    return JsonResponse({'deleted': True})




@login_required
@require_http_methods("POST")
@transaction.atomic
def item_create(request, pk):
    try:
        q = Quotation.objects.get(pk=pk)
    except Quotation.DoesNotExist:
        return JsonResponse({'error': 'Quotation not found'}, status=404)

    data = json.loads(request.body.decode('utf-8'))
    item = QuotationItem.objects.create(
        quotation = q,
        title = data.get("title", ""),
        description = data.get("description", ""),
        quantity = Decimal(str(data.get("quantity", 1))),
        unit_price = Decimal(str(data.get("unit_price", 0)))
    )
    return JsonResponse(item_to_dict(item), status=201)
    


@login_required
@require_http_methods(["PATCH", "DELETE"])
@transaction.atomic
def item_detail(request, qpk, ipk):
    try:
        q = Quotation.objects.get(pk=qpk)
    except Quotation.DoesNotExist:
        return JsonResponse({'error': 'Quotation not found'}, status=404)
    try:
        item = q.items.get(pk=ipk)
    except QuotationItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    

    if request.method == "PATCH":
        data = json.loads(request.body.decode('utf-8'))
        for field in ["title", "description"]:
            if field in data:
                setattr(item,field,data[field])

        if "quantity" in data:
            item.quantity = Decimal(str(data["quantity"]))
        if "unit_price" in data:
            item.unit_price = Decimal(str(data["unit_price"]))
        item.save()
        return JsonResponse(item_to_dict(item))
    
    #Delete
    item.delete()
    return JsonResponse({'deleted': True})


@login_required
def won_leads(request):
    leads = list(Lead.objects.filter(status="won").values("lead_id", "description"))
    return JsonResponse({"leads": leads})
