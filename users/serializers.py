from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email")
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use email and password for user creation
        user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'])
        return user
