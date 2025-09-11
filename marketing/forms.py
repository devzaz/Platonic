# marketing/forms.py
from django import forms
from .models import ContentAsset, Subscriber, MailingList, EmailCampaign

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = ContentAsset
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
            "body": forms.Textarea(attrs={"rows": 14, "class": "mt-1 block w-full p-2 border rounded-md border-gray-300 font-mono"}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.content_type = "email_template"  # force type
        if commit:
            obj.save()
        return obj

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email", "first_name", "mailing_lists"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
            "first_name": forms.TextInput(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
            "mailing_lists": forms.SelectMultiple(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
        }

class MailingListForm(forms.ModelForm):
    class Meta:
        model = MailingList
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
        }

class EmailCampaignForm(forms.ModelForm):
    class Meta:
        model = EmailCampaign
        fields = ["subject", "email_template", "mailing_list", "status"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
            "email_template": forms.Select(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
            "mailing_list": forms.Select(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
            "status": forms.Select(attrs={"class": "mt-1 block w-full p-2 border rounded-md border-gray-300"}),
        }

class AssetForm(forms.ModelForm):
    class Meta:
        model = ContentAsset
        fields = ["title", 'asset_file']
        widgets = {
            "title": forms.TextInput(attrs={'class':'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-pink-50 file:text-pink-700 hover:file:bg-pink-100',
                                            'id':'asset_file',
                                            'name':'file',
                                            }),
            "asset_file": forms.FileInput(attrs={
                'id':'asset-file',
                'name':'file',
                'class':'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-pink-50 file:text-pink-700 hover:file:bg-pink-100'
            })

        }


        def save(self, commit=False):
            obj = super.save(commit=False)
            obj.content_type = 'brand_visual'
            if commit:
                obj.save()
            return obj