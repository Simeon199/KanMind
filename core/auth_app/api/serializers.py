from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields = ['username', 'email', 'password', 'repeated_password']
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
        
        account = User(email=self.validated_data['email'], username=self.validated_data['username'])
        account.set_password(password)
        account.save()
        return account
    
# class LoginViewSerializer(serializers.Serializer):
#     username = serializers.URLField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = User.objects.get(username=data['username'])

#         # Additional validation logic (e.g. password confirmation)
#         if not data['password'] or not user.check_password(data['password']):
#             raise serializers.ValidationError("Invalid username or password")
#         return data