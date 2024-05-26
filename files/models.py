from django.db import models
from django.conf import settings

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    upload_complete = models.CharField(max_length=100)
    # status = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    s3_key = models.CharField(max_length=255, unique=True)  # Stores the S3 key for the file
    metadata = models.JSONField(null=True, blank=True)  # Stores additional metadata
    simple_url = models.URLField(null=True, blank=True)  # Stores the simple URL for the file
