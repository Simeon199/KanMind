import datetime
import pytest
from django.contrib.auth.models import User
from board_app.models import Board
from tasks_app.models import Task, TaskCommentsModel
from tasks_app.api.serializers import TaskSerializer, TaskCommentsSerializer


@pytest.fixture
def owner(db):
    return User.objects.create_user(username='Owner', email='owner@s.com', password='pass')


@pytest.fixture
def member(db):
    return User.objects.create_user(username='Member', email='member@s.com', password='pass')


@pytest.fixture
def outsider(db):
    return User.objects.create_user(username='Outsider', email='out@s.com', password='pass')


@pytest.fixture
def board(owner, member):
    b = Board.objects.create(title='Board', owner=owner)
    b.members.add(member)
    return b


@pytest.fixture
def task(board, member):
    return Task.objects.create(
        board=board, title='Task', description='Desc',
        status='to-do', priority='medium',
        assignee=member, reviewer=None,
        due_date=datetime.date(2026, 12, 31),
    )


# ---------- TaskSerializer ----------

@pytest.mark.django_db
class TestTaskSerializerOutput:
    def test_contains_expected_fields(self, task):
        data = TaskSerializer(task).data
        for field in ('id', 'title', 'status', 'priority', 'due_date', 'assignee', 'reviewer', 'comments_count'):
            assert field in data

    def test_assignee_is_nested_object(self, task, member):
        data = TaskSerializer(task).data
        assert isinstance(data['assignee'], dict)
        assert data['assignee']['id'] == member.id

    def test_assignee_id_excluded_from_output(self, task):
        data = TaskSerializer(task).data
        assert 'assignee_id' not in data

    def test_reviewer_id_excluded_from_output(self, task):
        data = TaskSerializer(task).data
        assert 'reviewer_id' not in data

    def test_comments_count_zero_initially(self, task):
        data = TaskSerializer(task).data
        assert data['comments_count'] == 0

    def test_comments_count_increases(self, task, member):
        TaskCommentsModel.objects.create(task=task, author=member, content='x')
        data = TaskSerializer(task).data
        assert data['comments_count'] == 1


@pytest.mark.django_db
class TestTaskSerializerValidation:
    def _valid_data(self, board, member):
        return {
            'board': board.id,
            'title': 'New',
            'description': 'A description',
            'status': 'to-do',
            'priority': 'low',
            'due_date': '2026-12-31',
            'assignee_id': member.id,
        }

    def test_valid_data_is_valid(self, board, member):
        serializer = TaskSerializer(data=self._valid_data(board, member))
        assert serializer.is_valid(), serializer.errors

    def test_assignee_not_member_is_invalid(self, board, outsider):
        data = self._valid_data(board, outsider)
        data['assignee_id'] = outsider.id
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()

    def test_reviewer_not_member_is_invalid(self, board, member, outsider):
        data = self._valid_data(board, member)
        data['reviewer_id'] = outsider.id
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()

    def test_board_change_on_existing_task_is_invalid(self, board, member, task, make_user):
        from board_app.models import Board as B
        other_owner = User.objects.create_user(username='O2', email='o2@t.com', password='p')
        other = B.objects.create(title='Other', owner=other_owner)
        serializer = TaskSerializer(
            instance=task,
            data={'board': other.id, 'title': 'T', 'description': '', 'status': 'to-do',
                  'priority': 'low', 'due_date': '2026-12-31'},
            partial=True,
        )
        assert not serializer.is_valid()

    @pytest.fixture
    def make_user(self, db):
        def _m(**kwargs):
            return User.objects.create_user(**kwargs)
        return _m


# ---------- TaskCommentsSerializer ----------

@pytest.mark.django_db
class TestTaskCommentsSerializer:
    def test_contains_expected_fields(self, task, member):
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='hello')
        data = TaskCommentsSerializer(comment).data
        for field in ('id', 'content', 'author', 'created_at'):
            assert field in data

    def test_author_is_string(self, task, member):
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='hello')
        data = TaskCommentsSerializer(comment).data
        assert isinstance(data['author'], str)

    def test_author_falls_back_to_username(self, task, member):
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='hi')
        data = TaskCommentsSerializer(comment).data
        assert data['author'] == member.username

    def test_author_uses_full_name_when_set(self, task, member):
        member.first_name = 'Max'
        member.last_name = 'Muster'
        member.save()
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='named')
        data = TaskCommentsSerializer(comment).data
        assert data['author'] == 'Max Muster'

    def test_id_is_read_only(self, task, member):
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='ro')
        serializer = TaskCommentsSerializer(comment, data={'id': 999, 'content': 'ro'}, partial=True)
        serializer.is_valid()
        assert serializer.validated_data.get('id') is None

    def test_empty_content_is_invalid(self):
        serializer = TaskCommentsSerializer(data={'content': ''})
        assert not serializer.is_valid()
