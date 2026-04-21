import pytest
from unittest.mock import MagicMock
from board_app.api.permissions import OwnerOfBoardPermission


def make_request(method, user):
    request = MagicMock()
    request.method = method
    request.user = user
    return request


def make_board(owner, members=None):
    board = MagicMock()
    board.owner = owner
    board.members.filter.return_value.exists.return_value = (
        (members is not None) and any(True for _ in members)
    )
    return board


@pytest.fixture
def permission():
    return OwnerOfBoardPermission()


@pytest.fixture
def owner_user(db):
    from django.contrib.auth.models import User
    return User.objects.create_user(username='owner', email='o@example.com', password='pass')


@pytest.fixture
def member_user(db):
    from django.contrib.auth.models import User
    user = User.objects.create_user(username='member', email='m@example.com', password='pass')
    return user


@pytest.fixture
def other_user(db):
    from django.contrib.auth.models import User
    return User.objects.create_user(username='other', email='x@example.com', password='pass')


def _board_with_real_members(owner, members=None):
    """Return a mock board that accurately reflects is_member for given users."""
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
    def test_owner_get_allowed(self, permission, owner_user):
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('GET', owner_user), None, board)

    def test_owner_patch_allowed(self, permission, owner_user):
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('PATCH', owner_user), None, board)

    def test_owner_delete_allowed(self, permission, owner_user):
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('DELETE', owner_user), None, board)

    def test_owner_put_allowed(self, permission, owner_user):
        board = _board_with_real_members(owner_user)
        assert permission.has_object_permission(make_request('PUT', owner_user), None, board)


@pytest.mark.django_db
class TestMemberPermissions:
    def test_member_get_allowed(self, permission, owner_user, member_user):
        board = _board_with_real_members(owner_user, members=[member_user])
        assert permission.has_object_permission(make_request('GET', member_user), None, board)

    def test_member_patch_allowed(self, permission, owner_user, member_user):
        board = _board_with_real_members(owner_user, members=[member_user])
        assert permission.has_object_permission(make_request('PATCH', member_user), None, board)

    def test_member_delete_denied(self, permission, owner_user, member_user):
        board = _board_with_real_members(owner_user, members=[member_user])
        assert not permission.has_object_permission(make_request('DELETE', member_user), None, board)

    def test_member_put_denied(self, permission, owner_user, member_user):
        board = _board_with_real_members(owner_user, members=[member_user])
        assert not permission.has_object_permission(make_request('PUT', member_user), None, board)


@pytest.mark.django_db
class TestOutsiderPermissions:
    def test_outsider_get_denied(self, permission, owner_user, other_user):
        board = _board_with_real_members(owner_user)
        assert not permission.has_object_permission(make_request('GET', other_user), None, board)

    def test_outsider_patch_denied(self, permission, owner_user, other_user):
        board = _board_with_real_members(owner_user)
        assert not permission.has_object_permission(make_request('PATCH', other_user), None, board)

    def test_outsider_delete_denied(self, permission, owner_user, other_user):
        board = _board_with_real_members(owner_user)
        assert not permission.has_object_permission(make_request('DELETE', other_user), None, board)
