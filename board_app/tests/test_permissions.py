"""
Unit tests for OwnerOfBoardPermission (board_app/api/permissions.py).

Tests exercise has_object_permission directly with mock requests and boards so
that the logic can be verified in isolation, without going through the full
HTTP stack.

Covers:
- Owner: allowed for GET, PATCH, PUT, and DELETE.
- Member: allowed for GET and PATCH; denied for PUT and DELETE.
- Outsider (neither owner nor member): denied for all methods.
"""

import pytest
from unittest.mock import MagicMock
from board_app.api.permissions import OwnerOfBoardPermission


def make_request(method, user):
    """
    Return a minimal mock request with the given HTTP method and user.
    """
    request = MagicMock()
    request.method = method
    request.user = user
    return request


def make_board(owner, members=None):
    """
    Return a mock board with the given owner and optional member list.
    """
    board = MagicMock()
    board.owner = owner
    board.members.filter.return_value.exists.return_value = (
        (members is not None) and any(True for _ in members)
    )
    return board


@pytest.fixture
def permission():
    """
    Return a fresh OwnerOfBoardPermission instance.
    """
    return OwnerOfBoardPermission()


@pytest.fixture
def owner_user(db):
    """
    Return a User who acts as the board owner.
    """
    from django.contrib.auth.models import User
    return User.objects.create_user(username='owner', email='o@example.com', password='pass')


@pytest.fixture
def member_user(db):
    """
    Return a User who acts as a board member.
    """
    from django.contrib.auth.models import User
    user = User.objects.create_user(username='member', email='m@example.com', password='pass')
    return user


@pytest.fixture
def other_user(db):
    """
    Return a User with no relation to the board.
    """
    from django.contrib.auth.models import User
    return User.objects.create_user(username='other', email='x@example.com', password='pass')


def _board_with_real_members(owner, members=None):
    """
    Return a mock board whose members.filter() accurately reflects the given member list.
    The side_effect on members.filter ensures that has_object_permission sees the
    correct exists() result for each user ID, mirroring real queryset behaviour.
    """
    from unittest.mock import MagicMock
    board = MagicMock()
    board.owner = owner
    member_ids = {u.id for u in (members or [])}

    def members_filter(id):
        qs = MagicMock()
        qs.exists.return_value = id in member_ids
        return qs

    board.members.filter.side_effect = lambda id: members_filter(id)
    return board


@pytest.mark.django_db
class TestOwnerPermissions:
    """
    Tests that the board owner is granted all HTTP methods.
    """

    def test_owner_get_allowed(self, permission, owner_user):
        """
        The board owner is permitted to perform a GET request.
        """
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('GET', owner_user), None, board)

    def test_owner_patch_allowed(self, permission, owner_user):
        """
        The board owner is permitted to perform a PATCH request.
        """
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('PATCH', owner_user), None, board)

    def test_owner_delete_allowed(self, permission, owner_user):
        """
        The board owner is permitted to perform a DELETE request.
        """
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('DELETE', owner_user), None, board)

    def test_owner_put_allowed(self, permission, owner_user):
        """
        The board owner is permitted to perform a PUT request.
        """
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('PUT', owner_user), None, board)


@pytest.mark.django_db
class TestMemberPermissions:
    """
    Tests that board members are granted read and partial-update access only.
    """

    def test_member_get_allowed(self, permission, owner_user, member_user):
        """
        A board member is permitted to perform a GET request.
        """
        board = _board_with_real_members(owner_user, members=[member_user])
        assert permission.has_object_permission(make_request('GET', member_user), None, board)

    def test_member_patch_allowed(self, permission, owner_user, member_user):
        """
        A board member is permitted to perform a PATCH request.
        """
        board = _board_with_real_members(owner_user, members=[member_user])
        assert permission.has_object_permission(make_request('PATCH', member_user), None, board)

    def test_member_delete_denied(self, permission, owner_user, member_user):
        """
        A board member is denied permission to perform a DELETE request.
        """
        board = _board_with_real_members(owner_user, members=[member_user])
        assert not permission.has_object_permission(make_request('DELETE', member_user), None, board)

    def test_member_put_denied(self, permission, owner_user, member_user):
        """
        A board member is denied permission to perform a PUT request.
        """
        board = _board_with_real_members(owner_user, members=[member_user])
        assert not permission.has_object_permission(make_request('PUT', member_user), None, board)


@pytest.mark.django_db
class TestOutsiderPermissions:
    """
    Tests that users with no board relationship are denied all methods.
    """

    def test_outsider_get_denied(self, permission, owner_user, other_user):
        """
        A user with no board relationship is denied permission to perform a GET request.
        """
        board = _board_with_real_members(owner_user)
        assert not permission.has_object_permission(make_request('GET', other_user), None, board)

    def test_outsider_patch_denied(self, permission, owner_user, other_user):
        """
        A user with no board relationship is denied permission to perform a PATCH request.
        """
        board = _board_with_real_members(owner_user)
        assert not permission.has_object_permission(make_request('PATCH', other_user), None, board)

    def test_outsider_delete_denied(self, permission, owner_user, other_user):
        """
        A user with no board relationship is denied permission to perform a DELETE request.
        """
        board = _board_with_real_members(owner_user)
        assert not permission.has_object_permission(make_request('DELETE', other_user), None, board)
