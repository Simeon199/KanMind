"""
Unit tests for auth_app serializers.

Covers:
- RegistrationSerializer: validation (matching passwords, unique email), user
  creation, and exclusion of the password from serialized output.
- CustomAuthTokenSerializer: resolution of valid credentials to a User instance,
  and appropriate errors for a wrong password or unknown email.
"""

import pytest
from django.contrib.auth.models import User
from auth_app.api.serializers import RegistrationSerializer, CustomAuthTokenSerializer


@pytest.mark.django_db
class TestRegistrationSerializer:
    """Unit tests for RegistrationSerializer."""

    def _valid_data(self):
        """Return a complete, valid input dictionary for RegistrationSerializer."""
        return {
            'fullname': 'Test User',
            'email': 'test@example.com',
            'password': 'pass1234',
            'repeated_password': 'pass1234',
        }

    def test_valid_data_is_valid(self):
        """The serializer reports no errors when all required fields are correct."""
        serializer = RegistrationSerializer(data=self._valid_data())
        assert serializer.is_valid()

    def test_creates_user(self):
        """Calling save() persists a new User with the correct email and username."""
        serializer = RegistrationSerializer(data=self._valid_data())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        assert User.objects.filter(email='test@example.com').exists()
        assert user.username == 'Test User'

    def test_password_mismatch_is_invalid(self):
        """The serializer is invalid and returns an 'error' key when passwords differ."""
        data = self._valid_data()
        data['repeated_password'] = 'mismatch'
        serializer = RegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert 'error' in serializer.errors

    def test_duplicate_email_is_invalid(self):
        """The serializer is invalid when the email address is already registered."""
        User.objects.create_user(username='Existing', email='test@example.com', password='pass')
        serializer = RegistrationSerializer(data=self._valid_data())
        assert not serializer.is_valid()

    def test_password_not_returned(self):
        """The serialized output does not expose the password field."""
        serializer = RegistrationSerializer(data=self._valid_data())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        assert 'password' not in serializer.data


@pytest.mark.django_db
class TestCustomAuthTokenSerializer:
    """Unit tests for CustomAuthTokenSerializer."""

    @pytest.fixture(autouse=True)
    def create_user(self):
        """Create a standard user available to all tests in this class."""
        self.user = User.objects.create_user(
            username='Auth User',
            email='auth@example.com',
            password='correctpass',
        )

    def test_valid_credentials_return_user(self):
        """Valid email and password resolve to the corresponding User instance."""
        serializer = CustomAuthTokenSerializer(data={'email': 'auth@example.com', 'password': 'correctpass'})
        assert serializer.is_valid()
        assert serializer.validated_data['user'] == self.user

    def test_wrong_password_is_invalid(self):
        """The serializer is invalid and returns a 'password' error for a wrong password."""
        serializer = CustomAuthTokenSerializer(data={'email': 'auth@example.com', 'password': 'wrong'})
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_unknown_email_is_invalid(self):
        """The serializer is invalid and returns an 'email' error for an unregistered email."""
        serializer = CustomAuthTokenSerializer(data={'email': 'ghost@example.com', 'password': 'any'})
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
