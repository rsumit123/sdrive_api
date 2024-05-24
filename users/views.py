from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, RegisterSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    


class CustomAuthToken(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

