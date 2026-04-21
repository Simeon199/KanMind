import datetime
import pytest
from rest_framework.test import APIClient
from tasks_app.models import Task
from .conftest import TASKS_LIST_URL


@pytest.mark.django_db
class TestTaskListAuthentication:
    def test_unauthenticated_returns_401(self):
        response = APIClient().get(TASKS_LIST_URL)
        assert response.status_code == 401

    def test_unauthenticated_post_returns_401(self):
        response = APIClient().post(TASKS_LIST_URL, {}, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestTaskListFiltering:
    def test_member_sees_tasks_on_their_board(self, member, task, auth_client):
        response = auth_client(member).get(TASKS_LIST_URL)
        assert response.status_code == 200
        ids = [t['id'] for t in response.data]
        assert task.id in ids

    def test_owner_sees_tasks_on_their_board(self, owner, task, auth_client):
        response = auth_client(owner).get(TASKS_LIST_URL)
        assert response.status_code == 200
        ids = [t['id'] for t in response.data]
        assert task.id in ids

    def test_outsider_cannot_see_tasks(self, outsider, task, auth_client):
        response = auth_client(outsider).get(TASKS_LIST_URL)
        # Outsider has no board context → IsMemberOfBoard denies at view level
        assert response.status_code in (200, 403)
        if response.status_code == 200:
            ids = [t['id'] for t in response.data]
            assert task.id not in ids

    def test_no_duplicate_tasks(self, owner, board, auth_client):
        board.members.add(owner)
        task = Task.objects.create(
            board=board, title='Dup Task', description='A description',
            status='to-do', priority='low',
            due_date=datetime.date(2026, 12, 31),
        )
        response = auth_client(owner).get(TASKS_LIST_URL)
        ids = [t['id'] for t in response.data]
        assert ids.count(task.id) == 1


@pytest.mark.django_db
class TestTaskCreate:
    def _payload(self, board):
        return {
            'board': board.id,
            'title': 'New Task',
            'description': 'A description',
            'status': 'to-do',
            'priority': 'low',
            'due_date': '2026-12-31',
        }

    def test_member_can_create_task(self, member, board, auth_client):
        response = auth_client(member).post(TASKS_LIST_URL, self._payload(board), format='json')
        assert response.status_code == 201

    def test_owner_can_create_task(self, owner, board, auth_client):
        response = auth_client(owner).post(TASKS_LIST_URL, self._payload(board), format='json')
        assert response.status_code == 201

    def test_outsider_cannot_create_task(self, outsider, board, auth_client):
        response = auth_client(outsider).post(TASKS_LIST_URL, self._payload(board), format='json')
        assert response.status_code in (403, 404)

    def test_created_task_saved_in_db(self, member, board, auth_client):
        auth_client(member).post(TASKS_LIST_URL, self._payload(board), format='json')
        assert Task.objects.filter(title='New Task').exists()

    def test_response_contains_expected_fields(self, member, board, auth_client):
        response = auth_client(member).post(TASKS_LIST_URL, self._payload(board), format='json')
        for field in ('id', 'title', 'status', 'priority', 'due_date'):
            assert field in response.data

    def test_assignee_must_be_board_member(self, owner, board, outsider, auth_client):
        payload = self._payload(board)
        payload['assignee_id'] = outsider.id
        response = auth_client(owner).post(TASKS_LIST_URL, payload, format='json')
        assert response.status_code == 400

    def test_reviewer_must_be_board_member(self, owner, board, outsider, auth_client):
        payload = self._payload(board)
        payload['reviewer_id'] = outsider.id
        response = auth_client(owner).post(TASKS_LIST_URL, payload, format='json')
        assert response.status_code == 400

    def test_assignee_as_board_member_accepted(self, owner, member, board, auth_client):
        payload = self._payload(board)
        payload['assignee_id'] = member.id
        response = auth_client(owner).post(TASKS_LIST_URL, payload, format='json')
        assert response.status_code == 201

    def test_missing_title_returns_400(self, member, board, auth_client):
        payload = self._payload(board)
        del payload['title']
        response = auth_client(member).post(TASKS_LIST_URL, payload, format='json')
        assert response.status_code == 400
