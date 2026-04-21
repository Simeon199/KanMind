import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from board_app.models import Board


@pytest.fixture
def make_user(db):
    counter = {'n': 0}

    def _make(username=None, email=None, password='testpass123'):
        counter['n'] += 1
        n = counter['n']
        user = User.objects.create_user(
            username=username or f'User {n}',
            email=email or f'user{n}@example.com',
            password=password,
        )
        Token.objects.create(user=user)
        return user

    return _make


@pytest.fixture
def owner(make_user):
    return make_user(username='Owner', email='owner@example.com')


@pytest.fixture
def member(make_user):
    return make_user(username='Member', email='member@example.com')


@pytest.fixture
def outsider(make_user):
    return make_user(username='Outsider', email='outsider@example.com')


@pytest.fixture
def board(owner, member):
    b = Board.objects.create(title='Test Board', owner=owner)
    b.members.add(member)
    return b


@pytest.fixture
def auth_client():
    def _client(user):
        client = APIClient()
        token = Token.objects.get(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return client

    return _client
