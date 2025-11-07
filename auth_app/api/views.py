from .serializers import RegistrationSerializer, CustomAuthTokenSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import generics, status

def get_token_response(user):
    """
    Generate a token response dictionary for the given user.

    Args:
        user (User): The user instance.

    Returns:
        dict: Contains the authentication token, user's full name, email, and user ID.
    """
    token, created = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'fullname': user.username,
        'email': user.email,
        'user_id': user.id
    }

class RegistrationView(generics.CreateAPIView):
    """
    API view for user registration.

    Allows any user to register by sending a POST request with the required data.
    Returns a token and user information upon successful registration.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def get(self, request):
        """
        Return a simple message indicating the registration form endpoint.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: A message about the registration form.
        """
        return Response({"message": "Registration form"})

    def create(self, request, *args, **kwargs):
        """
        Handle user registration.

        Validates the incoming data, creates a new user, and returns a token and user info.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: Token and user information if successful, otherwise validation errors.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = get_token_response(user)
        return Response(data, status=201)
    
class CustomLoginView(APIView):
    """
    API view for user login.

    Allows any user to log in by sending a POST request with credentials.
    Returns a token and user information upon successful authentication.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Return a simple message indicating the login form endpoint.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: A message about the login form.
        """
        return Response({"message": "Login form"})

    def post(self, request):
        """
        Handle user login.

        Validates the credentials, authenticates the user, and returns a token and user info.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            Response: Token and user information if successful, otherwise validation errors.
        """
        serializer = CustomAuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            data = get_token_response(user)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)