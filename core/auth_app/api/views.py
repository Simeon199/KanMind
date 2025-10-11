# app/auth_user_views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

class RegistrationView(APIView):
    permission_classes=[AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        # Validate and create the user *before* issuing tokens

        try:
            user_data = serializer.save() # This automatically handles password hashing

            token, created = Token.objects.get_or_create(user=user_data)
            data = {
                'token': token.key,
                'username': user_data.username,
                'email': user_data.email
                # Consider adding additional fields like name if needed later
            }
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
        return Response(data, status=201) # Use 201 Created status on successful registration 

    # def post(self, request):
    #     serializer = RegistrationView(data=request.data)
    #     data = {}

    #     if serializer.is_valid():
    #         saved_account = serializer.save()
    #         token, created = Token.objects.get_or_create(user=saved_account)
    #         data = {
    #             'token': token.key,
    #             'username': saved_account.username,
    #             'email': saved_account.email
    #         }
    #     else:
    #         data=serializer.errors
    #     return Response(data)
    

class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        data = {}

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email
            }
        else:
            data=serializer.errors

        return Response(data)