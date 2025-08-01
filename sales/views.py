from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LeadForm, ContactForm
from .models import Lead, Contact
from django.http import JsonResponse, HttpResponseNotAllowed



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




