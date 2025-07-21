from django import forms
from .models import Contact,Quotation, Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model=Lead
        fields = ['Contact', 'status', 'source', 'estimated_value', 'assign_to', 'description']
        widgets = {
            'Contact': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2', 'id':'lead-status'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2','id':"lead-status"}),
            'source': forms.TextInput(attrs={'type':"text", 'id':"lead-source", 'class':"mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2", 'placeholder':"e.g., Website, Referral"}),
            'estimated_value': forms.NumberInput(attrs={'type':"number", 'id':"lead-value", 'class':"block w-full rounded-md border-gray-300 pl-7 p-2", 'placeholder':"Please add decimal number like 5000.00"}),
            'assign_to': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2','id':"lead-assigned"}),
            'description': forms.Textarea(attrs={'type':"text", 'id':"lead-description", 'class':"mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2", 'placeholder':"Description", 'rows': 3}),
        }

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['lead','quotation_id', 'status','issue_date', 'details','created_by']
        widgets = {
            'Contact': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2', 'id':'quotation-contact'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2','id':"quotation-status"}),
            'description': forms.Textarea(attrs={'type':"text", 'id':"quotation-description", 'class':"mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2", 'placeholder':"Description", 'rows': 3}),
            'amount': forms.NumberInput(attrs={'type':"number", 'id':"quotation-amount", 'class':"block w-full rounded-md border-gray-300 pl-7 p-2", 'placeholder':"Please add decimal number like 5000.00"}),
        }