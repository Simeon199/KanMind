from rest_framework import serializers
from django.contrib.auth import authenticate
from auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    Serializes all fields of the UserProfile model.
    """
    class Meta:
        model = UserProfile
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles validation and creation of new users.
    """
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

    def validate(self, data):
        """
        Validate the input data for registration.
        Ensures passwords match and the email is unique.
        
        Args:
            data (dict): The input data
        
        Returns:
            dict: The validated data
        """
        self._validate_passwords(data)
        self._validate_email(data['email'])
        return data
    
    def _validate_passwords(self, data):
        """
        Validate that the passwords match.
        Args: 
           data (dict): The input data.
        Raises:
           serializers.ValidationError: If passwords do not match.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'error': 'Passwords do not match'})
        
    def _validate_email(self, email):
        """
        Validate that the email is unique.

        Args:
           email (str): The email to validate.

        Raises: 
           serializers.ValidationError: If the email already exists.  
        """
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        
    def create(self, validated_data):
        """
        Create a new user with the validated data.

        Args: 
           validated_data (dict); The validated data.
        
        Returns:
           User: The created user instance.
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class CustomAuthTokenSerializer(serializers.Serializer): 
    """
    Serializer for custom authentication tokens.
    Handles validation of user credentials and returns the authenticated user.
    """
    email = serializers.EmailField(label="email", write_only=True)
    password = serializers.CharField(label="password", style={'input_type': 'password'}, trim_whitespace=False, write_only=True)
    
    def validate(self, attrs):
        """
        Validate the user credentials.

        Args:
           attrs (dict): The input data.

        Returns:
           dict: The validated data with the authenticated user.
        Raises:
           serializers.ValidationError: If the credentials are invalid.
        """
        user = self._get_user_by_email(attrs.get('email'))
        self._validate_credentials(user, attrs.get('password'))
        attrs['user'] = user
        return attrs
    
    def _get_user_by_email(self,email):
        """
        Retrieve the user by email.

        Args:
           email (str): The email to look up.
        
        Returns: 
           User: The user instance.

        Raises:
           serializers.ValidationError: If no user with the email exists.
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'No user with this email'})
        
    def _validate_credentials(self, user, password):
        """
        Validate the user's credentials.

        Args:
           user (User): The user instance.
           password (str): The password to validate.

        Raises: 
           serializers.ValidationError: If the credentials are invalid.
        """
        if not authenticate(username=user.username, password=password):
            raise serializers.ValidationError({'password': 'Invalid credentials'})