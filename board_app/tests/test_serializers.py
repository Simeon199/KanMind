"""
Unit tests for board_app serializers.

Covers:
- BoardSerializer: presence of all expected fields; correctness of computed fields
  (member_count, ticket_count, tasks_to_do_count, tasks_high_prio_count, owner_id);
  absence of sensitive data.
- BoardUpdateSerializer: the write-only 'members' field is excluded from the
  response; 'owner_data' and 'members_data' are present with correct content.
- SingleBoardSerializer: 'tasks' and 'members' fields are included; member objects
  expose the email address.
"""

import pytest
import datetime
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from board_app.models import Board
from board_app.api.serializers import BoardSerializer, SingleBoardSerializer, BoardUpdateSerializer
from tasks_app.models import Task


@pytest.fixture
def owner(db):
    """
    Return a User who acts as the board owner.
    """
    return User.objects.create_user(username='Owner', email='owner@example.com', password='pass')


@pytest.fixture
def member(db):
    """
    Return a User who is a member of the test board.
    """
    return User.objects.create_user(username='Member', email='member@example.com', password='pass')


@pytest.fixture
def board(owner, member):
    """
    Return a Board owned by `owner` with `member` added as a member.
    """
    b = Board.objects.create(title='Serializer Board', owner=owner)
    b.members.add(member)
    return b


@pytest.fixture
def request_for(owner):
    """
    Return a GET request with `owner` as the authenticated user, for serializer context.
    """
    factory = APIRequestFactory()
    request = factory.get('/')
    request.user = owner
    return request


@pytest.mark.django_db
class TestBoardSerializerFields:
    """
    Tests for the output fields and computed values of BoardSerializer.
    """

    def test_contains_expected_fields(self, board, request_for):
        """
        All expected fields are present in the serialized output.
        """
        serializer = BoardSerializer(board, context={'request': request_for})
        for field in ('id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'):
            assert field in serializer.data

    def test_member_count_is_correct(self, board):
        """
        'member_count' reflects the actual number of members on the board.
        """
        serializer = BoardSerializer(board)
        assert serializer.data['member_count'] == 1

    def test_ticket_count_zero_when_no_tasks(self, board):
        """
        'ticket_count' is zero when the board has no associated tasks.
        """
        serializer = BoardSerializer(board)
        assert serializer.data['ticket_count'] == 0

    def test_tasks_to_do_count_reflects_tasks(self, board, member):
        """
        'tasks_to_do_count' increments when a task with status 'to-do' is added.
        """
        Task.objects.create(
            board=board, title='T1', description='',
            status='to-do', priority='low',
            assignee=None, reviewer=None,
            due_date=datetime.date.today(),
        )
        serializer = BoardSerializer(board)
        assert serializer.data['tasks_to_do_count'] == 1

    def test_tasks_high_prio_count_reflects_tasks(self, board, member):
        """
        'tasks_high_prio_count' increments when a task with priority 'high' is added.
        """
        Task.objects.create(
            board=board, title='T2', description='',
            status='in_progress', priority='high',
            assignee=None, reviewer=None,
            due_date=datetime.date.today(),
        )
        serializer = BoardSerializer(board)
        assert serializer.data['tasks_high_prio_count'] == 1

    def test_owner_id_matches(self, board, owner):
        """
        'owner_id' matches the primary key of the board's owner.
        """
        serializer = BoardSerializer(board)
        assert serializer.data['owner_id'] == owner.id

    def test_password_not_exposed(self, board):
        """
        The serialized output does not contain any password-related data.
        """
        serializer = BoardSerializer(board)
        assert 'password' not in str(serializer.data)


@pytest.mark.django_db
class TestBoardUpdateSerializerResponse:
    """
    Tests for the response shape of BoardUpdateSerializer (used on PATCH).
    """

    def test_members_write_field_excluded_from_output(self, board):
        """
        The write-only 'members' field is stripped from the serialized output.
        """
        serializer = BoardUpdateSerializer(board)
        assert 'members' not in serializer.data

    def test_owner_data_present(self, board):
        """
        The response includes an 'owner_data' object with owner details.
        """
        serializer = BoardUpdateSerializer(board)
        assert 'owner_data' in serializer.data

    def test_members_data_present(self, board):
        """
        The response includes a 'members_data' list with member details.
        """
        serializer = BoardUpdateSerializer(board)
        assert 'members_data' in serializer.data

    def test_members_data_contains_member(self, board, member):
        """
        The 'members_data' list contains the board member's user ID.
        """
        serializer = BoardUpdateSerializer(board)
        ids = [m['id'] for m in serializer.data['members_data']]
        assert member.id in ids


@pytest.mark.django_db
class TestSingleBoardSerializer:
    """
    Tests for SingleBoardSerializer, used for full board detail responses (GET).
    """

    def test_contains_tasks_field(self, board):
        """
        The serialized output includes a 'tasks' field.
        """
        serializer = SingleBoardSerializer(board)
        assert 'tasks' in serializer.data

    def test_contains_members_field(self, board):
        """
        The serialized output includes a 'members' field.
        """
        serializer = SingleBoardSerializer(board)
        assert 'members' in serializer.data

    def test_tasks_empty_when_no_tasks(self, board):
        """
        'tasks' is an empty list when the board has no associated tasks.
        """
        serializer = SingleBoardSerializer(board)
        assert serializer.data['tasks'] == []

    def test_member_detail_contains_email(self, board, member):
        """
        Each member object in 'members' exposes the user's email address.
        """
        serializer = SingleBoardSerializer(board)
        emails = [m['email'] for m in serializer.data['members']]
        assert member.email in emails
