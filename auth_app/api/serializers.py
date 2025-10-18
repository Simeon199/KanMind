from rest_framework import serializers
from django.contrib.auth import authenticate
# from rest_framework.authtoken.serializers import AuthTokenSerializer 
from auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='username')
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def save(self):
        password = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']

        if password != repeated_password:
            raise serializers.ValidationError({'error': 'passwords dont match'})
        
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError('Email already exists')
        
        account = User(email=self.validated_data['email'], 
                       username=self.validated_data['username']
        )
        account.set_password(password)
        account.save()
        return account
    
class CustomAuthTokenSerializer(serializers.Serializer): # Ehemals AuthTokenSerializer
    email = serializers.EmailField(label="email", write_only=True)
    password = serializers.CharField(label="password", style={'input_type': 'password'}, trim_whitespace=False, write_only=True)
    
    # Find the user by email
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'No user with this email'})

        # Authenticate using username and password
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError({'password': 'Invalid credentials'})
        
        attrs['user'] = user
        return attrs
    
    # fullname = serializers.CharField(label='fullname', write_only=True)
    # username = None

    # def validate(self, attrs):
    #     attrs['username'] = attrs.pop('fullname')
    #     return super().validate(attrs)