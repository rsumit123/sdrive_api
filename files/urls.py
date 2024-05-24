from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, FileUploadView

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('', include(router.urls)),
    # path('simple-get/', SimpleGetView.as_view(), name='simple-get'),

]
