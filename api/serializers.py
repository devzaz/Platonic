from rest_framework import serializers
from .models import ContactUs, Career
import filetype

ALLOWED_MIMES = {
    "application/pdf",
    # DOCX: OOXML is a Zip container; filetype returns application/zip for many zip-based docs.
    # We'll handle DOCX by extension check below.
    "application/msword",
}
ALLOWED_EXTS = {".pdf", ".doc", ".docx"}


PHONE_HELP = "Please include your country code. E.g., +1234567890"

class ContactUsSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(help_text=PHONE_HELP)

    class Meta:
        model = ContactUs
        fields = [
            "uid", "name", "phone", "email", "message", "created_at", "updated_at"
        ]
        read_only_fields = ["uid", "created_at", "updated_at"]



class CareerSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(help_text=PHONE_HELP)
    resume = serializers.FileField(write_only=True)


    class Meta:
        model = Career
        fields = [
        "uid", "full_name", "email", "phone", "portfolio_link", "linkedin",
        "position", "resume", "cover_letter", "created_at", "updated_at"
        ]
        read_only_fields = ("uid", "created_at", "updated_at")




    def validate_resume(self, file):
        # 5 MB limit
        max_mb = 5
        if file.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Resume file too large (>{max_mb}MB)")

        # Try to detect by signature
        kind = filetype.guess(file.read(262))  # read a small chunk
        file.seek(0)

        # Accept if clearly PDF or DOC (legacy)
        if kind and kind.mime in ALLOWED_MIMES:
            return file

        # Accept DOCX by extension (signature is ZIP)
        name = (file.name or "").lower()
        if name.endswith(".docx"):
            return file

        # Fallback: simple extension check for PDF/DOC
        if any(name.endswith(ext) for ext in ALLOWED_EXTS):
            return file

        raise serializers.ValidationError("Only PDF, DOC, or DOCX allowed.")