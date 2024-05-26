from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

admin.site.site_header = (
    "SDrive Administration"  # default: "Django Administration"
)
admin.site.index_title = "SDrive Administration"  # default: "Site administration"
admin.site.site_title = (
    "Welcome to SDrive Management Portal"  # default: "Django site admin"
)

admin.sites.AdminSite.site_header = "SDrive Administration"
admin.sites.AdminSite.site_title = "SDrive Administration"
admin.sites.AdminSite.index_title = "Welcome to SDrive Management Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('files.urls')),  # Ensure this line includes 'files.urls'
    path('api/auth/', include('users.urls')),
]
