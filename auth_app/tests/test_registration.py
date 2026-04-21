import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


REGISTRATION_URL = reverse('registration')


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def valid_payload():
    return {
        'fullname': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'securepass123',
        'repeated_password': 'securepass123',
    }


@pytest.mark.django_db
class TestRegistrationSuccess:
    def test_returns_201(self, client, valid_payload):
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 201

    def test_response_contains_token(self, client, valid_payload):
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert 'token' in response.data

    def test_response_contains_user_fields(self, client, valid_payload):
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.data['email'] == valid_payload['email']
        assert response.data['fullname'] == valid_payload['fullname']
        assert 'user_id' in response.data

    def test_user_created_in_db(self, client, valid_payload):
        client.post(REGISTRATION_URL, valid_payload, format='json')
        assert User.objects.filter(email=valid_payload['email']).exists()

    def test_password_is_hashed(self, client, valid_payload):
        client.post(REGISTRATION_URL, valid_payload, format='json')
        user = User.objects.get(email=valid_payload['email'])
        assert user.check_password(valid_payload['password'])

    def test_token_created_in_db(self, client, valid_payload):
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        user = User.objects.get(email=valid_payload['email'])
        assert Token.objects.filter(user=user).exists()
        assert Token.objects.get(user=user).key == response.data['token']

    def test_password_not_in_response(self, client, valid_payload):
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert 'password' not in response.data
        assert 'repeated_password' not in response.data


@pytest.mark.django_db
class TestRegistrationValidation:
    def test_mismatched_passwords_returns_400(self, client, valid_payload):
        valid_payload['repeated_password'] = 'different'
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_duplicate_email_returns_400(self, client, valid_payload):
        client.post(REGISTRATION_URL, valid_payload, format='json')
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_missing_email_returns_400(self, client, valid_payload):
        del valid_payload['email']
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_missing_password_returns_400(self, client, valid_payload):
        del valid_payload['password']
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_missing_fullname_returns_400(self, client, valid_payload):
        del valid_payload['fullname']
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_empty_payload_returns_400(self, client):
        response = client.post(REGISTRATION_URL, {}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRegistrationGet:
    def test_get_returns_200(self, client):
        response = client.get(REGISTRATION_URL)
        assert response.status_code == 200

    def test_get_returns_message(self, client):
        response = client.get(REGISTRATION_URL)
        assert 'message' in response.data
