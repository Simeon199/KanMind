from rest_framework import serializers
from django.contrib.auth import authenticate
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

    # def validate(self, data):
    #     self._validate_passwords(data)
    #     self._validate_email(data['email'])
    #     return data
    
    # def _validate_passwords(self, data):
    #     if data['password'] != data['repeated_password']:
    #         raise serializers.ValidationError({'error': 'Passwords do not match'})
        
    # def _validate_email(self, email):
    #     if User.objects.filter(email=email).exists():
    #         raise serializers.ValidationError({'email': 'Email already exists'})
        
    # def create(self, validated_data):
    #     user = User(
    #         email=validated_data['email'],
    #         username=validated_data['username']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user

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
    
class CustomAuthTokenSerializer(serializers.Serializer): 
    email = serializers.EmailField(label="email", write_only=True)
    password = serializers.CharField(label="password", style={'input_type': 'password'}, trim_whitespace=False, write_only=True)
    
    # def validate(self, attrs):
    #     user = self._get_user_by_email(attrs.get('email'))
    #     self._validate_credentials(user, attrs.get('password'))
    #     attrs['user'] = user
    #     return attrs
    
    # def _get_user_by_email(self,email):
    #     try:
    #         return User.objects.get(email=email)
    #     except User.DoesNotExist:
    #         raise serializers.ValidationError({'email': 'No user with this email'})
        
    # def _validate_credentials(self, user, password):
    #     if not authenticate(username=user.username, password=password):
    #         raise serializers.ValidationError({'password': 'Invalid credentials'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'No user with this email'})

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError({'password': 'Invalid credentials'})
        
        attrs['user'] = user
        return attrs