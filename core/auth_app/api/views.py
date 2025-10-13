from django.shortcuts import render, redirect
from .serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import generics

class RegistrationView(APIView):
    permission_classes=[AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get(self, request):
        return Response({"message": "Registration form"})

    def post(self, request):
        serializer_class = RegistrationSerializer
        serializer = serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        try:
            user_data = serializer.save()
            token, created = Token.objects.get_or_create(user=user_data)
            data = {
                'token': token.key,
                'username': user_data.username,
                'email': user_data.email
            }
            return Response(data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Login form"})

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email
            }
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)