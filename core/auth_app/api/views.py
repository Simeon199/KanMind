# app/auth_user_views.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

class RegistrationView(APIView):
    permission_classes=[AllowAny]

    def post(self, request):
        serializer = RegistrationView(data=request.data)
        data = {}

        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email
            }
        else:
            data=serializer.errors
        return Response(data)


# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user_data = {
#                 'username': form.cleaned_data['username'],
#                 'email': form.cleaned_data['email'],
#                 'password': form.cleaned_data['password'],
#             }
#             new_user = User.objects.create_user(
#                 username=user_data['username'],
#                 email=user_data['email'],
#                 password=form.cleaned_data['password'],
#             )
#             return redirect('registration_success')
#         else:
#             return render(request, 'auth/register.html', {'form': form})
#     return render(request, 'auth/register.html', {'form': UserCreationForm()})