import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from board_app.models import Board
from board_app.api.serializers import BoardSerializer, SingleBoardSerializer, BoardUpdateSerializer
from tasks_app.models import Task
import datetime


@pytest.fixture
def owner(db):
    return User.objects.create_user(username='Owner', email='owner@example.com', password='pass')


@pytest.fixture
def member(db):
    return User.objects.create_user(username='Member', email='member@example.com', password='pass')


@pytest.fixture
def board(owner, member):
    b = Board.objects.create(title='Serializer Board', owner=owner)
    b.members.add(member)
    return b


@pytest.fixture
def request_for(owner):
    factory = APIRequestFactory()
    request = factory.get('/')
    request.user = owner
    return request


@pytest.mark.django_db
class TestBoardSerializerFields:
    def test_contains_expected_fields(self, board, request_for):
        serializer = BoardSerializer(board, context={'request': request_for})
        for field in ('id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'):
            assert field in serializer.data

    def test_member_count_is_correct(self, board):
        serializer = BoardSerializer(board)
        assert serializer.data['member_count'] == 1

    def test_ticket_count_zero_when_no_tasks(self, board):
        serializer = BoardSerializer(board)
        assert serializer.data['ticket_count'] == 0

    def test_tasks_to_do_count_reflects_tasks(self, board, member):
        Task.objects.create(
            board=board, title='T1', description='',
            status='to-do', priority='low',
            assignee=None, reviewer=None,
            due_date=datetime.date.today(),
        )
        serializer = BoardSerializer(board)
        assert serializer.data['tasks_to_do_count'] == 1

    def test_tasks_high_prio_count_reflects_tasks(self, board, member):
        Task.objects.create(
            board=board, title='T2', description='',
            status='in_progress', priority='high',
            assignee=None, reviewer=None,
            due_date=datetime.date.today(),
        )
        serializer = BoardSerializer(board)
        assert serializer.data['tasks_high_prio_count'] == 1

    def test_owner_id_matches(self, board, owner):
        serializer = BoardSerializer(board)
        assert serializer.data['owner_id'] == owner.id

    def test_password_not_exposed(self, board):
        serializer = BoardSerializer(board)
        assert 'password' not in str(serializer.data)


@pytest.mark.django_db
class TestBoardUpdateSerializerResponse:
    def test_members_write_field_excluded_from_output(self, board):
        serializer = BoardUpdateSerializer(board)
        assert 'members' not in serializer.data

    def test_owner_data_present(self, board):
        serializer = BoardUpdateSerializer(board)
        assert 'owner_data' in serializer.data

    def test_members_data_present(self, board):
        serializer = BoardUpdateSerializer(board)
        assert 'members_data' in serializer.data

    def test_members_data_contains_member(self, board, member):
        serializer = BoardUpdateSerializer(board)
        ids = [m['id'] for m in serializer.data['members_data']]
        assert member.id in ids


@pytest.mark.django_db
class TestSingleBoardSerializer:
    def test_contains_tasks_field(self, board):
        serializer = SingleBoardSerializer(board)
        assert 'tasks' in serializer.data

    def test_contains_members_field(self, board):
        serializer = SingleBoardSerializer(board)
        assert 'members' in serializer.data

    def test_tasks_empty_when_no_tasks(self, board):
        serializer = SingleBoardSerializer(board)
        assert serializer.data['tasks'] == []

    def test_member_detail_contains_email(self, board, member):
        serializer = SingleBoardSerializer(board)
        emails = [m['email'] for m in serializer.data['members']]
        assert member.email in emails
