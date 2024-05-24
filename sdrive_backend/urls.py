from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('files.urls')),  # Ensure this line includes 'files.urls'
    path('api/auth/', include('users.urls')),
]
