from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.conf import settings
import boto3
from .models import UploadedFile
from .serializers import UploadedFileSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
import requests


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES['file']
        tier = request.data.get('tier', 'standard')
        # user = get_user_model().objects.get(email="rsumit123@gmail.com")
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=403)
        
        username = user.email.split('@')[0]+"-"+user.email.split('@')[1].split('.')[0]

        s3_key = f"{username}/{file_obj.name}"

        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_S3_REGION_NAME)

        try:
            s3.upload_fileobj(
                file_obj,
                settings.AWS_STORAGE_BUCKET_NAME,
                s3_key,
                ExtraArgs={'StorageClass': 'GLACIER' if tier == 'glacier' else 'STANDARD'}
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        file_metadata = {
            'content_type': file_obj.content_type,
            'size': file_obj.size,
            'tier': tier
        }
        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        simple_url = requests.get(f"https://ks0bm06q4a.execute-api.us-west-2.amazonaws.com/dev?long_url={s3_url}").json()
        print(simple_url)
        simple_url = "https://simple-url.skdev.one/"+simple_url['short_url']

        uploaded_file = UploadedFile.objects.create(
            file_name=file_obj.name,
            user=user,
            s3_key=s3_key,
            metadata=file_metadata,
            simple_url=simple_url
        )

        return Response({'message': 'File uploaded successfully', 'file': UploadedFileSerializer(uploaded_file).data})


class FileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer

    def get_queryset(self):
        # user = get_user_model().objects.get(email="rsumit123@gmail.com")
        # print(self.request.user)
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def list_files(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=403)

        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_S3_REGION_NAME)

        response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=f"{user.username}/")
        files = [item['Key'] for item in response.get('Contents', []) if 'Contents' in response]
        for file in files:
            file_record = UploadedFile.objects.get(s3_key=file)
            file['simple_url'] = file_record.simple_url
            # file['metadata'] = file_record.metadata
        # print(file)

        return Response(files)

    @action(detail=True, methods=['get'])
    def download_file(self, request, pk=None):
        # user = get_user_model().objects.get(email="rsumit123@gmail.com")
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=403)

        try:
            file_record = UploadedFile.objects.get(pk=pk, user=user)
        except UploadedFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=404)

        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_S3_REGION_NAME)

        try:
            head_response = s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_record.s3_key)
            storage_class = head_response.get('StorageClass')

            if storage_class in ['GLACIER', 'DEEP_ARCHIVE']:
                if 'Restore' not in head_response or 'ongoing-request="true"' in head_response['Restore']:
                    # Initiate restore request if not already in progress
                    s3.restore_object(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=file_record.s3_key,
                        RestoreRequest={
                            'Days': 1,
                            'GlacierJobParameters': {'Tier': 'Standard'}
                        }
                    )
                    file_record.metadata['tier'] = 'unarchiving'
                    file_record.save()

                    return Response({'message': 'File is being restored. Please try again later.'}, status=202)
                else:
                    # Check if the restoration is complete
                    if 'ongoing-request="false"' in head_response['Restore']:
                        file_record.metadata['tier'] = 'standard'
                        file_record.save()
                    file_obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_record.s3_key)
                    # Read the binary data
                    file_data = file_obj['Body'].read()

                    # Create a Django HTTP response object for sending binary data
                    response = HttpResponse(file_data, content_type=file_record.metadata['content_type'])
                    response['Content-Disposition'] = f'attachment; filename="{file_record.file_name}"'
                    return response

                    # return Response({'message': 'File restoration is in progress. Please try again later.'}, status=202)
            else:
                # file_obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_record.s3_key)
                # response = Response(file_obj['Body'].read(), content_type=file_record.metadata['content_type'])
                # response['Content-Disposition'] = f'attachment; filename="{file_record.file_name}"'
                # return response

                file_obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_record.s3_key)
                # Read the binary data
                file_data = file_obj['Body'].read()

                # Create a Django HTTP response object for sending binary data
                response = HttpResponse(file_data, content_type=file_record.metadata['content_type'])
                response['Content-Disposition'] = f'attachment; filename="{file_record.file_name}"'
                return response


        except Exception as e:
            print(f"Error downloading file from S3: {e}")
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['get'])
    def refresh_file_metadata(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=403)

        try:
            file_record = UploadedFile.objects.get(pk=pk, user=user)
        except UploadedFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=404)

        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_S3_REGION_NAME)

        try:
            head_response = s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_record.s3_key)
            storage_class = head_response.get('StorageClass', 'STANDARD')

            if storage_class == 'STANDARD':
                file_record.metadata['tier'] = 'standard'
            elif storage_class in ['GLACIER', 'DEEP_ARCHIVE']:
                if 'Restore' in head_response and 'ongoing-request="true"' in head_response['Restore']:
                    file_record.metadata['tier'] = 'unarchiving'
                else:
                    file_record.metadata['tier'] = 'glacier'

            file_record.save()

            return Response({'message': 'Metadata refreshed', 'metadata': file_record.metadata}, status=200)

        except Exception as e:
            print(f"Error refreshing file metadata from S3: {e}")
            return Response({'error': str(e)}, status=500)
