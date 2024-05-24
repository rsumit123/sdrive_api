from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'file_name', 'upload_date', 'user', 's3_key', 'metadata', 'simple_url']
