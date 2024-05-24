from django.urls import path
from .views import RegisterView, UserView, CustomAuthToken

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserView.as_view(), name='user'),
    path('login/', CustomAuthToken.as_view(), name='login'),
]
