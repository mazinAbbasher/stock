from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        base_username = email.split('@')[0]
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already existed")
        username = base_username
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            # If username already exists, append a number to it
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = User.objects.create_user(username=username, email=email, password=password)

        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        # Move email to username for authentication backend compatibility
        attrs['username'] = attrs.get('email')
        return super().validate(attrs)

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

# Create your views here.
