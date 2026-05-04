# api/views_admin_uploads.py
import boto3
import os
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@staff_member_required
def presign_upload(request):
    filename = request.GET.get("filename")
    if not filename:
        return JsonResponse({"error": "Filename required"}, status=400)

    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        aws_access_key_id=os.environ.get("CLOUDFLARE_R2_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("CLOUDFLARE_SECRET_KEY"),
        endpoint_url=os.environ.get("CLOUDFLARE_R2_BUCKET_ENDPOINT"),
        region_name="auto",  # R2 doesn’t use AWS regions
    )

    bucket_name = os.environ.get("CLOUDFLARE_R2_BUCKET")
    object_key = f"uploads/{filename}"

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": bucket_name, "Key": object_key},
        ExpiresIn=3600,
    )

    public_url = f"{os.environ.get('CLOUDFLARE_R2_BUCKET_ENDPOINT')}/{bucket_name}/{object_key}"

    return JsonResponse({
        "upload_url": upload_url,
        "public_url": public_url,
    })
