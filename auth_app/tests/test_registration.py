"""
Tests for the user registration endpoint (POST/GET /api/registration/).
Covers:
- Successful registration: status code, response fields, DB state, token creation,
  password hashing, and exclusion of sensitive fields from the response.
- Input validation: mismatched passwords, duplicate email, missing required fields,
  and empty payload.
- GET behaviour: info message returned without authentication.
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


REGISTRATION_URL = reverse('registration')


@pytest.fixture
def client():
    """
    Return an unauthenticated API client.
    """
    return APIClient()


@pytest.fixture
def valid_payload():
    """
    Return a complete, valid registration payload.
    """
    return {
        'fullname': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'securepass123',
        'repeated_password': 'securepass123',
    }


@pytest.mark.django_db
class TestRegistrationSuccess:
    """
    Tests for successful user registration via POST /api/registration/.
    """

    def test_returns_201(self, client, valid_payload):
        """
        A valid registration request returns HTTP 201 Created.
        """
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 201

    def test_response_contains_token(self, client, valid_payload):
        """
        The response body includes an authentication token.
        """
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert 'token' in response.data

    def test_response_contains_user_fields(self, client, valid_payload):
        """
        The response body contains the email, fullname, and user_id of the new user.
        """
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.data['email'] == valid_payload['email']
        assert response.data['fullname'] == valid_payload['fullname']
        assert 'user_id' in response.data

    def test_user_created_in_db(self, client, valid_payload):
        """
        A new User record is persisted in the database after registration.
        """
        client.post(REGISTRATION_URL, valid_payload, format='json')
        assert User.objects.filter(email=valid_payload['email']).exists()

    def test_password_is_hashed(self, client, valid_payload):
        """
        The stored password is hashed, not stored in plain text.
        """
        client.post(REGISTRATION_URL, valid_payload, format='json')
        user = User.objects.get(email=valid_payload['email'])
        assert user.check_password(valid_payload['password'])

    def test_token_created_in_db(self, client, valid_payload):
        """
        A Token record is created in the database and matches the response token.
        """
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        user = User.objects.get(email=valid_payload['email'])
        assert Token.objects.filter(user=user).exists()
        assert Token.objects.get(user=user).key == response.data['token']

    def test_password_not_in_response(self, client, valid_payload):
        """
        Neither 'password' nor 'repeated_password' are exposed in the response.
        """
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert 'password' not in response.data
        assert 'repeated_password' not in response.data


@pytest.mark.django_db
class TestRegistrationValidation:
    """
    Tests for input validation on POST /api/registration/.
    """

    def test_mismatched_passwords_returns_400(self, client, valid_payload):
        """
        Registration fails with HTTP 400 when the two passwords do not match.
        """
        valid_payload['repeated_password'] = 'different'
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_duplicate_email_returns_400(self, client, valid_payload):
        """
        Registration fails with HTTP 400 when the email address is already in use.
        """
        client.post(REGISTRATION_URL, valid_payload, format='json')
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_missing_email_returns_400(self, client, valid_payload):
        """
        Registration fails with HTTP 400 when the email field is absent.
        """
        del valid_payload['email']
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_missing_password_returns_400(self, client, valid_payload):
        """
        Registration fails with HTTP 400 when the password field is absent.
        """
        del valid_payload['password']
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_missing_fullname_returns_400(self, client, valid_payload):
        """
        Registration fails with HTTP 400 when the fullname field is absent.
        """
        del valid_payload['fullname']
        response = client.post(REGISTRATION_URL, valid_payload, format='json')
        assert response.status_code == 400

    def test_empty_payload_returns_400(self, client):
        """
        Registration fails with HTTP 400 when the request body is empty.
        """
        response = client.post(REGISTRATION_URL, {}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRegistrationGet:
    """
    Tests for GET /api/registration/ (informational endpoint, no auth required).
    """

    def test_get_returns_200(self, client):
        """
        A GET request to the registration endpoint returns HTTP 200 OK.
        """
        response = client.get(REGISTRATION_URL)
        assert response.status_code == 200

    def test_get_returns_message(self, client):
        """
        The GET response contains a 'message' key.
        """
        response = client.get(REGISTRATION_URL)
        assert 'message' in response.data