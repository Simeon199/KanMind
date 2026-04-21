"""
Unit tests for tasks_app serializers.

Covers:
- TaskSerializer (output): presence of all expected fields; assignee and reviewer
  are serialized as nested objects; write-only ID fields are absent; comments_count
  reflects the actual number of comments.
- TaskSerializer (validation): valid data is accepted; assignee and reviewer must
  be board members; changing a task's board on update is forbidden.
- TaskCommentsSerializer: presence of all expected fields; the 'author' field is a
  string that falls back to username or uses first+last name when available;
  the 'id' field is read-only; empty content is invalid.
"""

import datetime
import pytest
from django.contrib.auth.models import User
from board_app.models import Board
from tasks_app.models import Task, TaskCommentsModel
from tasks_app.api.serializers import TaskSerializer, TaskCommentsSerializer


@pytest.fixture
def owner(db):
    """
    Return a User who acts as the board owner.
    """
    return User.objects.create_user(username='Owner', email='owner@s.com', password='pass')


@pytest.fixture
def member(db):
    """
    Return a User who is a member of the test board.
    """
    return User.objects.create_user(username='Member', email='member@s.com', password='pass')


@pytest.fixture
def outsider(db):
    """
    Return a User with no relationship to the test board.
    """
    return User.objects.create_user(username='Outsider', email='out@s.com', password='pass')


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
    Return a Task belonging to `board`, assigned to `member`, due 2026-12-31.
    """
    return Task.objects.create(
        board=board, title='Task', description='Desc',
        status='to-do', priority='medium',
        assignee=member, reviewer=None,
        due_date=datetime.date(2026, 12, 31),
    )


# ---------- TaskSerializer ----------

@pytest.mark.django_db
class TestTaskSerializerOutput:
    """
    Tests for the read-side output of TaskSerializer.
    """

    def test_contains_expected_fields(self, task):
        """
        All required fields are present in the serialized task output.
        """
        data = TaskSerializer(task).data
        for field in ('id', 'title', 'status', 'priority', 'due_date', 'assignee', 'reviewer', 'comments_count'):
            assert field in data

    def test_assignee_is_nested_object(self, task, member):
        """
        The 'assignee' field is serialized as a nested dict containing the user's ID.
        """
        data = TaskSerializer(task).data
        assert isinstance(data['assignee'], dict)
        assert data['assignee']['id'] == member.id

    def test_assignee_id_excluded_from_output(self, task):
        """
        The write-only 'assignee_id' field is absent from the serialized output.
        """
        data = TaskSerializer(task).data
        assert 'assignee_id' not in data

    def test_reviewer_id_excluded_from_output(self, task):
        """
        The write-only 'reviewer_id' field is absent from the serialized output.
        """
        data = TaskSerializer(task).data
        assert 'reviewer_id' not in data

    def test_comments_count_zero_initially(self, task):
        """
        'comments_count' is zero when the task has no comments.
        """
        data = TaskSerializer(task).data
        assert data['comments_count'] == 0

    def test_comments_count_increases(self, task, member):
        """
        'comments_count' increments when a comment is added to the task.
        """
        TaskCommentsModel.objects.create(task=task, author=member, content='x')
        data = TaskSerializer(task).data
        assert data['comments_count'] == 1


@pytest.mark.django_db
class TestTaskSerializerValidation:
    """
    Tests for the write-side validation logic of TaskSerializer.
    """

    def _valid_data(self, board, member):
        """
        Return a complete, valid input dictionary for TaskSerializer.
        """
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
        """
        The serializer reports no errors when all required fields are correct.
        """
        serializer = TaskSerializer(data=self._valid_data(board, member))
        assert serializer.is_valid(), serializer.errors

    def test_assignee_not_member_is_invalid(self, board, outsider):
        """
        The serializer is invalid when the assignee is not a member of the board.
        """
        data = self._valid_data(board, outsider)
        data['assignee_id'] = outsider.id
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()

    def test_reviewer_not_member_is_invalid(self, board, member, outsider):
        """
        The serializer is invalid when the reviewer is not a member of the board.
        """
        data = self._valid_data(board, member)
        data['reviewer_id'] = outsider.id
        serializer = TaskSerializer(data=data)
        assert not serializer.is_valid()

    def test_board_change_on_existing_task_is_invalid(self, board, member, task, make_user):
        """
        The serializer is invalid when attempting to change an existing task's board.
        """
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
        """
        Return a factory that creates a User with the given kwargs.
        """
        def _m(**kwargs):
            return User.objects.create_user(**kwargs)
        return _m


# ---------- TaskCommentsSerializer ----------

@pytest.mark.django_db
class TestTaskCommentsSerializer:
    """
    Tests for TaskCommentsSerializer.
    """

    def test_contains_expected_fields(self, task, member):
        """
        All required fields are present in the serialized comment output.
        """
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='hello')
        data = TaskCommentsSerializer(comment).data
        for field in ('id', 'content', 'author', 'created_at'):
            assert field in data

    def test_author_is_string(self, task, member):
        """
        The 'author' field is serialized as a plain string, not an object.
        """
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='hello')
        data = TaskCommentsSerializer(comment).data
        assert isinstance(data['author'], str)

    def test_author_falls_back_to_username(self, task, member):
        """
        'author' equals the user's username when first_name and last_name are not set.
        """
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='hi')
        data = TaskCommentsSerializer(comment).data
        assert data['author'] == member.username

    def test_author_uses_full_name_when_set(self, task, member):
        """
        'author' is the concatenation of first_name and last_name when both are set.
        """
        member.first_name = 'Max'
        member.last_name = 'Muster'
        member.save()
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='named')
        data = TaskCommentsSerializer(comment).data
        assert data['author'] == 'Max Muster'

    def test_id_is_read_only(self, task, member):
        """
        Supplying an 'id' value in input data does not affect the validated output.
        """
        comment = TaskCommentsModel.objects.create(task=task, author=member, content='ro')
        serializer = TaskCommentsSerializer(comment, data={'id': 999, 'content': 'ro'}, partial=True)
        serializer.is_valid()
        assert serializer.validated_data.get('id') is None

    def test_empty_content_is_invalid(self):
        """
        The serializer is invalid when the 'content' field is an empty string.
        """
        serializer = TaskCommentsSerializer(data={'content': ''})
        assert not serializer.is_valid()