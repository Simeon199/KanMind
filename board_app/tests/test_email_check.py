import pytest
from django.urls import reverse
from rest_framework.test import APIClient

EMAIL_CHECK_URL = reverse('email-check')


@pytest.mark.django_db
class TestEmailCheckAuthentication:
    def test_unauthenticated_returns_401(self):
        response = APIClient().get(EMAIL_CHECK_URL, {'email': 'any@example.com'})
        assert response.status_code == 401


@pytest.mark.django_db
class TestEmailCheckSuccess:
    def test_existing_email_returns_200(self, owner, auth_client):
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.status_code == 200

    def test_response_contains_id(self, owner, auth_client):
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.data['id'] == owner.id

    def test_response_contains_email(self, owner, auth_client):
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.data['email'] == owner.email

    def test_response_contains_fullname(self, owner, auth_client):
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert 'fullname' in response.data

    def test_fullname_falls_back_to_username(self, owner, auth_client):
        # owner has no first_name/last_name set → should use username
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': owner.email})
        assert response.data['fullname'] == owner.username

    def test_fullname_uses_first_and_last_name_when_set(self, owner, make_user, auth_client):
        user = make_user(email='named@example.com')
        user.first_name = 'Max'
        user.last_name = 'Mustermann'
        user.save()
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': 'named@example.com'})
        assert response.data['fullname'] == 'MaxMustermann'


@pytest.mark.django_db
class TestEmailCheckErrors:
    def test_unknown_email_returns_404(self, owner, auth_client):
        response = auth_client(owner).get(EMAIL_CHECK_URL, {'email': 'ghost@example.com'})
        assert response.status_code == 404

    def test_missing_email_param_returns_400(self, owner, auth_client):
        response = auth_client(owner).get(EMAIL_CHECK_URL)
        assert response.status_code == 400

    def test_missing_email_error_detail(self, owner, auth_client):
        response = auth_client(owner).get(EMAIL_CHECK_URL)
        assert 'detail' in response.data
