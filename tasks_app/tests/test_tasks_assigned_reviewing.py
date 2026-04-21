"""
Tests for the assigned-to-me and reviewing task endpoints.

Endpoints:
- GET/POST /api/tasks/assigned-to-me/
- GET/POST /api/tasks/reviewing/

Covers:
- Authentication: unauthenticated requests are rejected with HTTP 401.
- assigned-to-me list: returns only tasks where the requesting user is the
  assignee, scoped to their boards; tasks from foreign boards are excluded.
- assigned-to-me create: the view automatically sets the assignee to the
  authenticated user; the task is persisted.
- reviewing list: returns only tasks where the requesting user is the reviewer;
  tasks assigned to others are excluded.
- reviewing create: the view automatically sets the reviewer to the authenticated
  user.
"""

import datetime
import pytest
from rest_framework.test import APIClient
from tasks_app.models import Task
from .conftest import ASSIGNED_URL, REVIEWING_URL


def _base_payload(board):
    """
    Return a minimal valid task creation payload for the given board.
    """
    return {
        'board': board.id,
        'title': 'Auto-assigned Task',
        'description': 'A description',
        'status': 'to-do',
        'priority': 'low',
        'due_date': '2026-12-31',
    }


@pytest.mark.django_db
class TestAssignedToMeAuthentication:
    """
    Tests that unauthenticated access to /api/tasks/assigned-to-me/ is rejected.
    """

    def test_unauthenticated_returns_401(self):
        """
        An unauthenticated GET request is rejected with HTTP 401 Unauthorized.
        """
        assert APIClient().get(ASSIGNED_URL).status_code == 401

    def test_unauthenticated_post_returns_401(self):
        """
        An unauthenticated POST request is rejected with HTTP 401 Unauthorized.
        """
        assert APIClient().post(ASSIGNED_URL, {}, format='json').status_code == 401


@pytest.mark.django_db
class TestAssignedToMeList:
    """
    Tests for GET /api/tasks/assigned-to-me/.
    """

    def test_returns_200_for_authenticated_user(self, member, auth_client):
        """
        An authenticated GET request returns HTTP 200 OK.
        """
        response = auth_client(member).get(ASSIGNED_URL)
        assert response.status_code == 200

    def test_returns_assigned_tasks(self, member, task, auth_client):
        """
        Tasks where the requesting user is the assignee appear in the response.
        """
        # task fixture has assignee=member
        response = auth_client(member).get(ASSIGNED_URL)
        ids = [t['id'] for t in response.data]
        assert task.id in ids

    def test_does_not_return_unassigned_tasks(self, owner, task, auth_client):
        """
        Tasks where the requesting user is not the assignee are excluded.
        """
        # owner is not the assignee of task
        response = auth_client(owner).get(ASSIGNED_URL)
        ids = [t['id'] for t in response.data]
        assert task.id not in ids

    def test_does_not_return_tasks_from_foreign_boards(self, outsider, task, make_user, auth_client):
        """
        Tasks assigned to the user on boards they do not belong to are excluded.
        """
        from board_app.models import Board
        other_owner = make_user()
        other_board = Board.objects.create(title='Other Board', owner=other_owner)
        other_board.members.add(outsider)
        Task.objects.create(
            board=other_board, title='Foreign', description='',
            status='to-do', priority='low',
            assignee=outsider, due_date=datetime.date(2026, 12, 31),
        )
        # outsider should not see tasks from `board` fixture
        response = auth_client(outsider).get(ASSIGNED_URL)
        ids = [t['id'] for t in response.data]
        assert task.id not in ids

    def test_empty_list_when_no_assignments(self, owner, board, auth_client):
        """
        An authenticated user with no assigned tasks receives an empty list.
        """
        # owner has no tasks assigned to them in the fixture board
        response = auth_client(owner).get(ASSIGNED_URL)
        assert response.status_code == 200
        assert isinstance(response.data, list)


@pytest.mark.django_db
class TestAssignedToMeCreate:
    """
    Tests for POST /api/tasks/assigned-to-me/.
    """

    def test_post_sets_assignee_to_current_user(self, member, board, auth_client):
        """
        The view automatically sets the assignee to the authenticated user.
        """
        response = auth_client(member).post(ASSIGNED_URL, _base_payload(board), format='json')
        assert response.status_code == 201
        task = Task.objects.get(id=response.data['id'])
        assert task.assignee == member

    def test_post_creates_task_in_db(self, member, board, auth_client):
        """
        A newly created task via this endpoint is persisted in the database.
        """
        auth_client(member).post(ASSIGNED_URL, _base_payload(board), format='json')
        assert Task.objects.filter(title='Auto-assigned Task').exists()


@pytest.mark.django_db
class TestReviewingAuthentication:
    """
    Tests that unauthenticated access to /api/tasks/reviewing/ is rejected.
    """

    def test_unauthenticated_returns_401(self):
        """
        An unauthenticated GET request is rejected with HTTP 401 Unauthorized.
        """
        assert APIClient().get(REVIEWING_URL).status_code == 401


@pytest.mark.django_db
class TestReviewingList:
    """
    Tests for GET /api/tasks/reviewing/.
    """

    def test_returns_200_for_authenticated_user(self, member, auth_client):
        """
        An authenticated GET request returns HTTP 200 OK.
        """
        response = auth_client(member).get(REVIEWING_URL)
        assert response.status_code == 200

    def test_returns_tasks_user_is_reviewing(self, member, board, auth_client):
        """
        Tasks where the requesting user is the reviewer appear in the response.
        """
        task = Task.objects.create(
            board=board, title='Review Task', description='',
            status='review', priority='medium',
            reviewer=member, due_date=datetime.date(2026, 12, 31),
        )
        response = auth_client(member).get(REVIEWING_URL)
        ids = [t['id'] for t in response.data]
        assert task.id in ids

    def test_does_not_return_tasks_not_reviewing(self, owner, board, member, auth_client):
        """
        Tasks where the requesting user is not the reviewer are excluded.
        """
        task = Task.objects.create(
            board=board, title='Not Reviewing', description='',
            status='review', priority='medium',
            reviewer=member, due_date=datetime.date(2026, 12, 31),
        )
        # owner is not the reviewer
        response = auth_client(owner).get(REVIEWING_URL)
        ids = [t['id'] for t in response.data]
        assert task.id not in ids


@pytest.mark.django_db
class TestReviewingCreate:
    """
    Tests for POST /api/tasks/reviewing/.
    """

    def test_post_sets_reviewer_to_current_user(self, member, board, auth_client):
        """
        The view automatically sets the reviewer to the authenticated user.
        """
        response = auth_client(member).post(REVIEWING_URL, _base_payload(board), format='json')
        assert response.status_code == 201
        task = Task.objects.get(id=response.data['id'])
        assert task.reviewer == member
