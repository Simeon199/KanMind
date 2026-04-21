"""
Unit tests for tasks_app permission classes (tasks_app/api/permissions.py).

Tests exercise permission methods directly with mock requests and real database
objects so that the logic can be verified in isolation, without going through
the full HTTP stack.

Covers:
- IsMemberOfBoard (object level): owner and member are granted access; outsider
  is denied; permission works for both Task and TaskCommentsModel objects.
- IsMemberOfBoard (view level): board ID supplied in request data is resolved
  correctly; task PK in the URL is resolved to a board; no context returns False.
- IsTaskCreatorOrBoardOwner: only the board owner may delete a task; members and
  outsiders are denied; unauthenticated users are rejected at view level.
- IsCommentAuthor: only the comment author may delete; other users are denied.
"""

import datetime
import pytest
from unittest.mock import MagicMock
from django.contrib.auth.models import User
from board_app.models import Board
from tasks_app.models import Task, TaskCommentsModel
from tasks_app.api.permissions import (
    IsMemberOfBoard,
    IsTaskCreatorOrBoardOwner,
    IsCommentAuthor,
)


# ---------- Helpers ----------

def make_request(method, user):
    """
    Return a minimal mock request with the given HTTP method, user, and empty data dict.
    """
    req = MagicMock()
    req.method = method
    req.user = user
    req.data = {}
    return req


# ---------- Fixtures ----------

@pytest.fixture
def owner(db):
    """
    Return a User who acts as the board owner.
    """
    return User.objects.create_user(username='owner', email='owner@t.com', password='pass')


@pytest.fixture
def member(db):
    """
    Return a User who is a member of the test board.
    """
    return User.objects.create_user(username='member', email='member@t.com', password='pass')


@pytest.fixture
def outsider(db):
    """
    Return a User with no relationship to the test board.
    """
    return User.objects.create_user(username='outsider', email='out@t.com', password='pass')


@pytest.fixture
def board(owner, member):
    """
    Return a Board owned by `owner` with `member` added as a member.
    """
    b = Board.objects.create(title='Board', owner=owner)
    b.members.add(member)
    return b


@pytest.fixture
def task(board, member):
    """
    Return a Task belonging to `board`, due 2026-12-31.
    """
    return Task.objects.create(
        board=board, title='T', description='',
        status='to-do', priority='low',
        due_date=datetime.date(2026, 12, 31),
    )


@pytest.fixture
def comment(task, member):
    """
    Return a TaskCommentsModel written by `member` on `task`.
    """
    return TaskCommentsModel.objects.create(task=task, author=member, content='hi')


# ---------- IsMemberOfBoard ----------

@pytest.mark.django_db
class TestIsMemberOfBoardObjectPermission:
    """
    Tests for IsMemberOfBoard.has_object_permission with Task and comment objects.
    """

    def test_owner_has_permission(self, owner, task):
        """
        The board owner is granted object-level permission on the task.
        """
        perm = IsMemberOfBoard()
        assert perm.has_object_permission(make_request('GET', owner), None, task)

    def test_member_has_permission(self, member, task):
        """
        A board member is granted object-level permission on the task.
        """
        perm = IsMemberOfBoard()
        assert perm.has_object_permission(make_request('GET', member), None, task)

    def test_outsider_denied(self, outsider, task):
        """
        A user with no board membership is denied object-level permission on the task.
        """
        perm = IsMemberOfBoard()
        assert not perm.has_object_permission(make_request('GET', outsider), None, task)

    def test_works_for_comment_object(self, member, comment):
        """
        Object-level permission is granted to a member for a TaskCommentsModel object.
        """
        perm = IsMemberOfBoard()
        assert perm.has_object_permission(make_request('GET', member), None, comment)

    def test_outsider_denied_for_comment(self, outsider, comment):
        """
        A user with no board membership is denied object-level permission on a comment.
        """
        perm = IsMemberOfBoard()
        assert not perm.has_object_permission(make_request('GET', outsider), None, comment)


@pytest.mark.django_db
class TestIsMemberOfBoardViewPermission:
    """
    Tests for IsMemberOfBoard.has_permission with various request/view configurations.
    """

    def _make_view(self, pk=None, task_id=None):
        """
        Return a mock view whose kwargs contain the given pk and/or task_id values.
        """
        view = MagicMock()
        view.kwargs = {}
        if pk is not None:
            view.kwargs['pk'] = pk
        if task_id is not None:
            view.kwargs['task_id'] = task_id
        return view

    def test_board_id_in_data_member_allowed(self, member, board):
        """
        A board member is granted view-level permission when board ID is in request data.
        """
        perm = IsMemberOfBoard()
        req = make_request('POST', member)
        req.data = {'board': board.id}
        assert perm.has_permission(req, self._make_view())

    def test_board_id_in_data_outsider_denied(self, outsider, board):
        """
        An outsider is denied view-level permission even when board ID is in request data.
        """
        perm = IsMemberOfBoard()
        req = make_request('POST', outsider)
        req.data = {'board': board.id}
        assert not perm.has_permission(req, self._make_view())

    def test_task_pk_in_url_member_allowed(self, member, task):
        """
        A board member is granted view-level permission when the task PK is in the URL.
        """
        perm = IsMemberOfBoard()
        assert perm.has_permission(make_request('GET', member), self._make_view(pk=task.id))

    def test_task_pk_in_url_outsider_denied(self, outsider, task):
        """
        An outsider is denied view-level permission when the task PK is in the URL.
        """
        perm = IsMemberOfBoard()
        assert not perm.has_permission(make_request('GET', outsider), self._make_view(pk=task.id))

    def test_no_context_returns_false(self, member):
        """
        Permission is denied when neither board ID nor task PK can be resolved.
        """
        perm = IsMemberOfBoard()
        assert not perm.has_permission(make_request('GET', member), self._make_view())


# ---------- IsTaskCreatorOrBoardOwner ----------

@pytest.mark.django_db
class TestIsTaskCreatorOrBoardOwner:
    """
    Tests for IsTaskCreatorOrBoardOwner, which guards task DELETE operations.
    """

    def test_board_owner_can_delete(self, owner, task):
        """
        The board owner is granted object-level permission to delete the task.
        """
        perm = IsTaskCreatorOrBoardOwner()
        assert perm.has_object_permission(make_request('DELETE', owner), None, task)

    def test_member_cannot_delete(self, member, task):
        """
        A board member is denied permission to delete the task.
        """
        perm = IsTaskCreatorOrBoardOwner()
        assert not perm.has_object_permission(make_request('DELETE', member), None, task)

    def test_outsider_cannot_delete(self, outsider, task):
        """
        A user with no board membership is denied permission to delete the task.
        """
        perm = IsTaskCreatorOrBoardOwner()
        assert not perm.has_object_permission(make_request('DELETE', outsider), None, task)

    def test_unauthenticated_denied_at_view_level(self):
        """
        An unauthenticated user is denied at view level before object checks are reached.
        """
        perm = IsTaskCreatorOrBoardOwner()
        req = MagicMock()
        req.user = MagicMock(is_authenticated=False)
        assert not perm.has_permission(req, None)


# ---------- IsCommentAuthor ----------

@pytest.mark.django_db
class TestIsCommentAuthor:
    """
    Tests for IsCommentAuthor, which guards comment DELETE operations.
    """

    def test_author_has_permission(self, member, comment):
        """
        The comment author is granted object-level permission to delete the comment.
        """
        perm = IsCommentAuthor()
        assert perm.has_object_permission(make_request('DELETE', member), None, comment)

    def test_non_author_denied(self, owner, comment):
        """
        A user who is not the comment author is denied permission to delete it.
        """
        perm = IsCommentAuthor()
        assert not perm.has_object_permission(make_request('DELETE', owner), None, comment)

    def test_outsider_denied(self, outsider, comment):
        """
        A user with no board membership is denied permission to delete the comment.
        """
        perm = IsCommentAuthor()
        assert not perm.has_object_permission(make_request('DELETE', outsider), None, comment)