"""
URL patterns for the authentication app API.
This module defines the endpoints for user registration and login.
"""

from django.urls import path
from .views import RegistrationView, CustomLoginView

urlpatterns = [
    path('api/registration/', RegistrationView.as_view(), name='registration'), # Endpoint for user registration
    path('api/login/', CustomLoginView.as_view(), name='login') # Endpoint for user login
]