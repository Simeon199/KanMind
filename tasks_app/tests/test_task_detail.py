import pytest
from rest_framework.test import APIClient
from tasks_app.models import Task
from .conftest import task_detail_url


@pytest.mark.django_db
class TestTaskDetailAuthentication:
    def test_unauthenticated_get_returns_401(self, task):
        response = APIClient().get(task_detail_url(task.pk))
        assert response.status_code == 401

    def test_unauthenticated_patch_returns_401(self, task):
        response = APIClient().patch(task_detail_url(task.pk), {}, format='json')
        assert response.status_code == 401

    def test_unauthenticated_delete_returns_401(self, task):
        response = APIClient().delete(task_detail_url(task.pk))
        assert response.status_code == 401


@pytest.mark.django_db
class TestTaskDetailGet:
    def test_owner_can_retrieve_task(self, owner, task, auth_client):
        response = auth_client(owner).get(task_detail_url(task.pk))
        assert response.status_code == 200

    def test_member_can_retrieve_task(self, member, task, auth_client):
        response = auth_client(member).get(task_detail_url(task.pk))
        assert response.status_code == 200

    def test_outsider_cannot_retrieve_task(self, outsider, task, auth_client):
        response = auth_client(outsider).get(task_detail_url(task.pk))
        assert response.status_code in (403, 404)

    def test_nonexistent_task_returns_404(self, owner, auth_client):
        response = auth_client(owner).get(task_detail_url(99999))
        assert response.status_code == 404

    def test_response_contains_expected_fields(self, member, task, auth_client):
        response = auth_client(member).get(task_detail_url(task.pk))
        for field in ('id', 'title', 'status', 'priority', 'due_date', 'assignee', 'reviewer', 'comments_count'):
            assert field in response.data

    def test_assignee_returned_as_object(self, member, task, auth_client):
        response = auth_client(member).get(task_detail_url(task.pk))
        assert isinstance(response.data['assignee'], dict)
        assert response.data['assignee']['id'] == member.id

    def test_assignee_id_not_in_response(self, member, task, auth_client):
        response = auth_client(member).get(task_detail_url(task.pk))
        assert 'assignee_id' not in response.data


@pytest.mark.django_db
class TestTaskDetailPatch:
    def test_member_can_patch_title(self, member, task, auth_client):
        response = auth_client(member).patch(
            task_detail_url(task.pk), {'title': 'Updated Title'}, format='json'
        )
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.title == 'Updated Title'

    def test_owner_can_patch_task(self, owner, task, auth_client):
        response = auth_client(owner).patch(
            task_detail_url(task.pk), {'status': 'done'}, format='json'
        )
        assert response.status_code == 200

    def test_outsider_cannot_patch_task(self, outsider, task, auth_client):
        response = auth_client(outsider).patch(
            task_detail_url(task.pk), {'title': 'Hack'}, format='json'
        )
        assert response.status_code in (403, 404)

    def test_cannot_change_board(self, member, board, task, make_user, auth_client):
        other_board_owner = make_user()
        from board_app.models import Board
        other_board = Board.objects.create(title='Other', owner=other_board_owner)
        other_board.members.add(member)
        response = auth_client(member).patch(
            task_detail_url(task.pk), {'board': other_board.id}, format='json'
        )
        assert response.status_code == 400

    def test_patch_assignee_must_be_board_member(self, owner, task, outsider, auth_client):
        response = auth_client(owner).patch(
            task_detail_url(task.pk), {'assignee_id': outsider.id}, format='json'
        )
        assert response.status_code == 400

    def test_patch_assignee_to_valid_member(self, owner, member, task, auth_client):
        response = auth_client(owner).patch(
            task_detail_url(task.pk), {'assignee_id': member.id}, format='json'
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestTaskDetailDelete:
    def test_board_owner_can_delete_task(self, owner, task, auth_client):
        response = auth_client(owner).delete(task_detail_url(task.pk))
        assert response.status_code == 204
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_member_cannot_delete_task(self, member, task, auth_client):
        response = auth_client(member).delete(task_detail_url(task.pk))
        assert response.status_code == 403
        assert Task.objects.filter(pk=task.pk).exists()

    def test_outsider_cannot_delete_task(self, outsider, task, auth_client):
        response = auth_client(outsider).delete(task_detail_url(task.pk))
        assert response.status_code in (403, 404)

    def test_nonexistent_task_returns_404(self, owner, auth_client):
        response = auth_client(owner).delete(task_detail_url(99999))
        assert response.status_code == 404
