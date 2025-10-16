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
        
        account = User(email=self.validated_data['email'], fullname=self.validated_data['fullname'])
        account.set_password(password)
        account.save()
        return account