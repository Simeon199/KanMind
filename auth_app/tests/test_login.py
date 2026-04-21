import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


LOGIN_URL = reverse('login')


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def existing_user(db):
    user = User.objects.create_user(
        username='John Doe',
        email='john@example.com',
        password='testpass456',
    )
    Token.objects.create(user=user)
    return user


@pytest.mark.django_db
class TestLoginSuccess:
    def test_returns_200(self, client, existing_user):
        response = client.post(LOGIN_URL, {'email': existing_user.email, 'password': 'testpass456'}, format='json')
        assert response.status_code == 200

    def test_response_contains_token(self, client, existing_user):
        response = client.post(LOGIN_URL, {'email': existing_user.email, 'password': 'testpass456'}, format='json')
        assert 'token' in response.data

    def test_token_matches_db(self, client, existing_user):
        response = client.post(LOGIN_URL, {'email': existing_user.email, 'password': 'testpass456'}, format='json')
        db_token = Token.objects.get(user=existing_user).key
        assert response.data['token'] == db_token

    def test_response_contains_user_fields(self, client, existing_user):
        response = client.post(LOGIN_URL, {'email': existing_user.email, 'password': 'testpass456'}, format='json')
        assert response.data['email'] == existing_user.email
        assert response.data['fullname'] == existing_user.username
        assert response.data['user_id'] == existing_user.id

    def test_login_creates_token_if_missing(self, client, db):
        user = User.objects.create_user(
            username='No Token User',
            email='notoken@example.com',
            password='pass1234',
        )
        response = client.post(LOGIN_URL, {'email': 'notoken@example.com', 'password': 'pass1234'}, format='json')
        assert response.status_code == 200
        assert Token.objects.filter(user=user).exists()


@pytest.mark.django_db
class TestLoginValidation:
    def test_wrong_password_returns_400(self, client, existing_user):
        response = client.post(LOGIN_URL, {'email': existing_user.email, 'password': 'wrongpass'}, format='json')
        assert response.status_code == 400

    def test_wrong_password_error_message(self, client, existing_user):
        response = client.post(LOGIN_URL, {'email': existing_user.email, 'password': 'wrongpass'}, format='json')
        assert 'password' in response.data

    def test_unknown_email_returns_400(self, client, db):
        response = client.post(LOGIN_URL, {'email': 'nobody@example.com', 'password': 'anypass'}, format='json')
        assert response.status_code == 400

    def test_unknown_email_error_message(self, client, db):
        response = client.post(LOGIN_URL, {'email': 'nobody@example.com', 'password': 'anypass'}, format='json')
        assert 'email' in response.data

    def test_missing_email_returns_400(self, client, db):
        response = client.post(LOGIN_URL, {'password': 'anypass'}, format='json')
        assert response.status_code == 400

    def test_missing_password_returns_400(self, client, db):
        response = client.post(LOGIN_URL, {'email': 'someone@example.com'}, format='json')
        assert response.status_code == 400

    def test_empty_payload_returns_400(self, client, db):
        response = client.post(LOGIN_URL, {}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginGet:
    def test_get_returns_200(self, client):
        response = client.get(LOGIN_URL)
        assert response.status_code == 200

    def test_get_returns_message(self, client):
        response = client.get(LOGIN_URL)
        assert 'message' in response.data
