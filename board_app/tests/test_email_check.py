"""
Tests for the email-check endpoint (GET /api/email-check/).

Covers:
- Authentication: the endpoint requires a valid token.
- Successful lookup: a known email returns the user's id, email, and fullname;
  the fullname falls back to the username when first/last name are not set, and
  uses the concatenated name when they are.
- Error cases: an unknown email returns HTTP 404; a missing query parameter
  returns HTTP 400 with a 'detail' key in the response body.
"""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

EMAIL_CHECK_URL = reverse('email-check')


@pytest.mark.django_db
class TestEmailCheckAuthentication:
    """
    Tests that the email-check endpoint requires authentication.
    """

    def test_unauthenticated_returns_401(self):
        """An unauthenticated GET request is rejected with HTTP 401 Unauthorized."""
        response = APIClient().get(EMAIL_CHECK_URL, {'email': 'any@example.com'})
        assert response.status_code == 401


@pytest.mark.django_db
class TestEmailCheckSuccess:
    """
    Tests for successful user lookup via GET /api/email-check/?email=<address>.
    """

    def test_existing_email_returns_200(self, owner, auth_client):
        """
        A request for an existing email address returns HTTP 200 OK.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.status_code == 200

    def test_response_contains_id(self, owner, auth_client):
        """
        The response body includes the matched user's database ID.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.data['id'] == owner.id

    def test_response_contains_email(self, owner, auth_client):
        """
        The response body echoes back the queried email address.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.data['email'] == owner.email

    def test_response_contains_fullname(self, owner, auth_client):
        """
        The response body includes a 'fullname' field.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert 'fullname' in response.data

    def test_fullname_falls_back_to_username(self, owner, auth_client):
        """
        When a user has no first or last name, 'fullname' is set to their username.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.data['fullname'] == owner.username

    def test_fullname_uses_first_and_last_name_when_set(self, owner, make_user, auth_client):
        """
        When first_name and last_name are set, 'fullname' is their concatenation.
        """
        user = make_user(email='named@example.com')
        user.first_name = 'Max'
        user.last_name = 'Mustermann'
        user.save()
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': 'named@example.com'})
        assert response.data['fullname'] == 'MaxMustermann'


@pytest.mark.django_db
class TestEmailCheckErrors:
    """
    Tests for error responses from GET /api/email-check/.
    """

    def test_unknown_email_returns_404(self, owner, auth_client):
        """
        A request for an email address that does not belong to any user returns HTTP 404.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': 'ghost@example.com'})
        assert response.status_code == 404

    def test_missing_email_param_returns_400(self, owner, auth_client):
        """
        A request without the 'email' query parameter returns HTTP 400 Bad Request.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL)
        assert response.status_code == 400

    def test_missing_email_error_detail(self, owner, auth_client):
        """
        The HTTP 400 response for a missing email parameter contains a 'detail' key.
        """
        response = auth_client(owner).get(EMAIL_CHECK_URL)
        assert 'detail' in response.data