# api/forms.py
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
# import requests
# import base64

class R2PresignedFileField(forms.FileField):
    """
    A FileField that can accept either an uploaded file
    OR a Cloudflare R2 public URL (string).
    """

    def clean(self, data, initial=None):
        # Case 1: Real uploaded file → normal behavior
        if hasattr(data, "file") or hasattr(data, "chunks"):
            return super().clean(data, initial)

        # Case 2: String URL from hidden input
        if isinstance(data, str) and data.startswith("http"):
            # Convert the URL into a pseudo file Django can save
            filename = data.split("/")[-1]
            return SimpleUploadedFile(filename, b"", content_type="application/octet-stream")

        return super().clean(data, initial)
