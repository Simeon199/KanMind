"""
Shared pytest fixtures for board_app tests.
Provides reusable User, Board, and APIClient objects that are composed by the
individual test modules to avoid repetitive setup code.
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from board_app.models import Board


@pytest.fixture
def make_user(db):
    """
    Return a factory function that creates unique Users with Tokens on demand.
    Each call to the returned factory increments an internal counter so that
    auto-generated usernames and emails never collide within a single test.
    """
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
    """
    Return a User who acts as the board owner in tests.
    """
    return make_user(username='Owner', email='owner@example.com')


@pytest.fixture
def member(make_user):
    """
    Return a User who is a member (but not owner) of the test board.
    """
    return make_user(username='Member', email='member@example.com')


@pytest.fixture
def outsider(make_user):
    """
    Return a User who has no relationship to the test board.
    """
    return make_user(username='Outsider', email='outsider@example.com')


@pytest.fixture
def board(owner, member):
    """
    Return a Board owned by `owner` with `member` added as a member.
    """
    b = Board.objects.create(title='Test Board', owner=owner)
    b.members.add(member)
    return b


@pytest.fixture
def auth_client():
    """
    Return a factory function that produces an authenticated APIClient for a given user.
    The client uses Token authentication matching the user's existing Token record.
    """
    def _client(user):
        client = APIClient()
        token = Token.objects.get(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return client
    return _client