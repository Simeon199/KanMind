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
    def test_creates_guest_user(self):
        call_command('create_guest_user')
        assert User.objects.filter(email=GUEST_EMAIL).exists()

    def test_guest_user_has_correct_username(self):
        call_command('create_guest_user')
        user = User.objects.get(email=GUEST_EMAIL)
        assert user.username == GUEST_USERNAME

    def test_guest_user_password_is_valid(self):
        call_command('create_guest_user')
        user = User.objects.get(email=GUEST_EMAIL)
        assert user.check_password(GUEST_PASSWORD)

    def test_guest_user_token_created(self):
        call_command('create_guest_user')
        user = User.objects.get(email=GUEST_EMAIL)
        assert Token.objects.filter(user=user).exists()

    def test_command_is_idempotent(self):
        call_command('create_guest_user')
        call_command('create_guest_user')
        assert User.objects.filter(email=GUEST_EMAIL).count() == 1


@pytest.mark.django_db
class TestGuestLogin:
    def test_guest_can_login(self):
        call_command('create_guest_user')
        client = APIClient()
        response = client.post(LOGIN_URL, {'email': GUEST_EMAIL, 'password': GUEST_PASSWORD}, format='json')
        assert response.status_code == 200

    def test_guest_login_returns_token(self):
        call_command('create_guest_user')
        client = APIClient()
        response = client.post(LOGIN_URL, {'email': GUEST_EMAIL, 'password': GUEST_PASSWORD}, format='json')
        assert 'token' in response.data
        assert response.data['email'] == GUEST_EMAIL
