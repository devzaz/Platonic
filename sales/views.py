from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LeadForm
from .models import Lead, Contact



@login_required(login_url='login')
def dashboard(request):
    leads = Lead.objects.all()
    contacts = Contact.objects.all()


    lead_form = LeadForm()
    context = {
        'lead_form': lead_form,
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

