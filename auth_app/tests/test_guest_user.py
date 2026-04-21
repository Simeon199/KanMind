"""
Tests for the guest user feature.

Covers:
- create_guest_user management command: correct user creation, username, password,
  token generation, and idempotency (running twice must not create duplicates).
- Guest login via POST /api/login/: the pre-seeded guest account can authenticate
  and receives a valid token in return.
"""

import pytest
from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse


LOGIN_URL = reverse('login')

GUEST_EMAIL = 'max@mustermann.de'
GUEST_PASSWORD = 'asdasdasd'
GUEST_USERNAME = 'Max Mustermann'


@pytest.mark.django_db
class TestCreateGuestUserCommand:
    """
    Tests for the create_guest_user management command.
    """

    def test_creates_guest_user(self):
        """
        Running the command creates a User with the expected guest email.
        """
        call_command('create_guest_user')
        assert User.objects.filter(email=GUEST_EMAIL).exists()

    def test_guest_user_has_correct_username(self):
        """
        The created guest user has the expected username.
        """
        call_command('create_guest_user')
        user = User.objects.get(email=GUEST_EMAIL)
        assert user.username == GUEST_USERNAME

    def test_guest_user_password_is_valid(self):
        """
        The guest user's password is stored as a valid hash matching the known plain-text password.
        """
        call_command('create_guest_user')
        user = User.objects.get(email=GUEST_EMAIL)
        assert user.check_password(GUEST_PASSWORD)

    def test_guest_user_token_created(self):
        """
        A Token record is created for the guest user when the command runs.
        """
        call_command('create_guest_user')
        user = User.objects.get(email=GUEST_EMAIL)
        assert Token.objects.filter(user=user).exists()

    def test_command_is_idempotent(self):
        """
        Running the command twice does not create duplicate guest users.
        """
        call_command('create_guest_user')
        call_command('create_guest_user')
        assert User.objects.filter(email=GUEST_EMAIL).count() == 1


@pytest.mark.django_db
class TestGuestLogin:
    """
    Tests for logging in with the guest account via POST /api/login/.
    """

    def test_guest_can_login(self):
        """
        The guest account can authenticate and receives HTTP 200 OK.
        """
        call_command('create_guest_user')
        client = APIClient()
        response = client.post(LOGIN_URL, {'email': GUEST_EMAIL, 'password': GUEST_PASSWORD}, format='json')
        assert response.status_code == 200

    def test_guest_login_returns_token(self):
        """
        The login response includes a token and the guest email address.
        """
        call_command('create_guest_user')
        client = APIClient()
        response = client.post(LOGIN_URL, {'email': GUEST_EMAIL, 'password': GUEST_PASSWORD}, format='json')
        assert 'token' in response.data
        assert response.data['email'] == GUEST_EMAIL
