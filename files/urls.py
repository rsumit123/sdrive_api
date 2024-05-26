from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, FileUploadView, GeneratePresignedUrlView


router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('', include(router.urls)),
    path('presign/', GeneratePresignedUrlView.as_view(), name='generate-presign-url'),
    # path('simple-get/', SimpleGetView.as_view(), name='simple-get'),

]
