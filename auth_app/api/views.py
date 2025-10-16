from .serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import generics, status

def get_token_response(user):
    token, created = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'fullname': user.fullname,
        'email': user.email,
        'user_id': user.user_id
    }

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Registration form"})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = get_token_response(user)
        return Response(data, status=201)
    
class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Login form"})

    def post(self, request):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            data = get_token_response(user)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)