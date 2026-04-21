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
    req = MagicMock()
    req.method = method
    req.user = user
    req.data = {}
    return req


# ---------- Fixtures ----------

@pytest.fixture
def owner(db):
    return User.objects.create_user(username='owner', email='owner@t.com', password='pass')


@pytest.fixture
def member(db):
    return User.objects.create_user(username='member', email='member@t.com', password='pass')


@pytest.fixture
def outsider(db):
    return User.objects.create_user(username='outsider', email='out@t.com', password='pass')


@pytest.fixture
def board(owner, member):
    b = Board.objects.create(title='Board', owner=owner)
    b.members.add(member)
    return b


@pytest.fixture
def task(board, member):
    return Task.objects.create(
        board=board, title='T', description='',
        status='to-do', priority='low',
        due_date=datetime.date(2026, 12, 31),
    )


@pytest.fixture
def comment(task, member):
    return TaskCommentsModel.objects.create(task=task, author=member, content='hi')


# ---------- IsMemberOfBoard ----------

@pytest.mark.django_db
class TestIsMemberOfBoardObjectPermission:
    def test_owner_has_permission(self, owner, task):
        perm = IsMemberOfBoard()
        assert perm.has_object_permission(make_request('GET', owner), None, task)

    def test_member_has_permission(self, member, task):
        perm = IsMemberOfBoard()
        assert perm.has_object_permission(make_request('GET', member), None, task)

    def test_outsider_denied(self, outsider, task):
        perm = IsMemberOfBoard()
        assert not perm.has_object_permission(make_request('GET', outsider), None, task)

    def test_works_for_comment_object(self, member, comment):
        perm = IsMemberOfBoard()
        assert perm.has_object_permission(make_request('GET', member), None, comment)

    def test_outsider_denied_for_comment(self, outsider, comment):
        perm = IsMemberOfBoard()
        assert not perm.has_object_permission(make_request('GET', outsider), None, comment)


@pytest.mark.django_db
class TestIsMemberOfBoardViewPermission:
    def _make_view(self, pk=None, task_id=None):
        view = MagicMock()
        view.kwargs = {}
        if pk is not None:
            view.kwargs['pk'] = pk
        if task_id is not None:
            view.kwargs['task_id'] = task_id
        return view

    def test_board_id_in_data_member_allowed(self, member, board):
        perm = IsMemberOfBoard()
        req = make_request('POST', member)
        req.data = {'board': board.id}
        assert perm.has_permission(req, self._make_view())

    def test_board_id_in_data_outsider_denied(self, outsider, board):
        perm = IsMemberOfBoard()
        req = make_request('POST', outsider)
        req.data = {'board': board.id}
        assert not perm.has_permission(req, self._make_view())

    def test_task_pk_in_url_member_allowed(self, member, task):
        perm = IsMemberOfBoard()
        assert perm.has_permission(make_request('GET', member), self._make_view(pk=task.id))

    def test_task_pk_in_url_outsider_denied(self, outsider, task):
        perm = IsMemberOfBoard()
        assert not perm.has_permission(make_request('GET', outsider), self._make_view(pk=task.id))

    def test_no_context_returns_false(self, member):
        perm = IsMemberOfBoard()
        assert not perm.has_permission(make_request('GET', member), self._make_view())


# ---------- IsTaskCreatorOrBoardOwner ----------

@pytest.mark.django_db
class TestIsTaskCreatorOrBoardOwner:
    def test_board_owner_can_delete(self, owner, task):
        perm = IsTaskCreatorOrBoardOwner()
        assert perm.has_object_permission(make_request('DELETE', owner), None, task)

    def test_member_cannot_delete(self, member, task):
        perm = IsTaskCreatorOrBoardOwner()
        assert not perm.has_object_permission(make_request('DELETE', member), None, task)

    def test_outsider_cannot_delete(self, outsider, task):
        perm = IsTaskCreatorOrBoardOwner()
        assert not perm.has_object_permission(make_request('DELETE', outsider), None, task)

    def test_unauthenticated_denied_at_view_level(self):
        perm = IsTaskCreatorOrBoardOwner()
        req = MagicMock()
        req.user = MagicMock(is_authenticated=False)
        assert not perm.has_permission(req, None)


# ---------- IsCommentAuthor ----------

@pytest.mark.django_db
class TestIsCommentAuthor:
    def test_author_has_permission(self, member, comment):
        perm = IsCommentAuthor()
        assert perm.has_object_permission(make_request('DELETE', member), None, comment)

    def test_non_author_denied(self, owner, comment):
        perm = IsCommentAuthor()
        assert not perm.has_object_permission(make_request('DELETE', owner), None, comment)

    def test_outsider_denied(self, outsider, comment):
        perm = IsCommentAuthor()
        assert not perm.has_object_permission(make_request('DELETE', outsider), None, comment)
