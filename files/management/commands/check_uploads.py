from django.core.management.base import BaseCommand
from files.models import UploadedFile  # Adjust the import path according to your project structure
import boto3
from django.conf import settings
from files.utils import generate_simple_url

class Command(BaseCommand):
    help = 'Checks pending uploads and updates their status'

    def handle(self, *args, **options):
        s3_client = boto3.client('s3',
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                 region_name=settings.AWS_S3_REGION_NAME)
        pending_files = UploadedFile.objects.filter(upload_complete="pending")

        for file in pending_files:
            try:
                response = s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file.s3_key)
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    file.upload_complete = "complete"
                    file.metadata.update({"content_type": response['ContentType']})
                    file.simple_url = generate_simple_url(file.s3_key)
                    file.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated file: {file.s3_key}'))
            except s3_client.exceptions.ClientError as e:
                self.stdout.write(self.style.ERROR(f'Failed to update file: {file.s3_key} , got error {e}'))
