import pytest
from rest_framework.test import APIClient
from tasks_app.models import TaskCommentsModel
from .conftest import task_comments_url, task_comment_detail_url


@pytest.mark.django_db
class TestCommentListAuthentication:
    def test_unauthenticated_get_returns_401(self, task):
        response = APIClient().get(task_comments_url(task.pk))
        assert response.status_code == 401

    def test_unauthenticated_post_returns_401(self, task):
        response = APIClient().post(task_comments_url(task.pk), {'content': 'x'}, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestCommentList:
    def test_member_can_list_comments(self, member, task, comment, auth_client):
        response = auth_client(member).get(task_comments_url(task.pk))
        assert response.status_code == 200

    def test_owner_can_list_comments(self, owner, task, comment, auth_client):
        response = auth_client(owner).get(task_comments_url(task.pk))
        assert response.status_code == 200

    def test_outsider_cannot_list_comments(self, outsider, task, comment, auth_client):
        response = auth_client(outsider).get(task_comments_url(task.pk))
        assert response.status_code in (403, 404)

    def test_returns_existing_comment(self, member, task, comment, auth_client):
        response = auth_client(member).get(task_comments_url(task.pk))
        ids = [c['id'] for c in response.data]
        assert comment.id in ids

    def test_response_contains_expected_fields(self, member, task, comment, auth_client):
        response = auth_client(member).get(task_comments_url(task.pk))
        first = response.data[0]
        for field in ('id', 'content', 'author', 'created_at'):
            assert field in first


@pytest.mark.django_db
class TestCommentCreate:
    def test_member_can_add_comment(self, member, task, auth_client):
        response = auth_client(member).post(
            task_comments_url(task.pk), {'content': 'New comment'}, format='json'
        )
        assert response.status_code == 201

    def test_owner_can_add_comment(self, owner, task, auth_client):
        response = auth_client(owner).post(
            task_comments_url(task.pk), {'content': 'Owner comment'}, format='json'
        )
        assert response.status_code == 201

    def test_outsider_cannot_add_comment(self, outsider, task, auth_client):
        response = auth_client(outsider).post(
            task_comments_url(task.pk), {'content': 'Hack'}, format='json'
        )
        assert response.status_code in (403, 404)

    def test_author_set_to_authenticated_user(self, member, task, auth_client):
        auth_client(member).post(
            task_comments_url(task.pk), {'content': 'Mine'}, format='json'
        )
        c = TaskCommentsModel.objects.get(content='Mine')
        assert c.author == member

    def test_comment_linked_to_correct_task(self, member, task, auth_client):
        auth_client(member).post(
            task_comments_url(task.pk), {'content': 'Linked'}, format='json'
        )
        c = TaskCommentsModel.objects.get(content='Linked')
        assert c.task == task

    def test_empty_content_returns_400(self, member, task, auth_client):
        response = auth_client(member).post(
            task_comments_url(task.pk), {'content': ''}, format='json'
        )
        assert response.status_code == 400

    def test_missing_content_returns_400(self, member, task, auth_client):
        response = auth_client(member).post(
            task_comments_url(task.pk), {}, format='json'
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestCommentDetailAuthentication:
    def test_unauthenticated_get_returns_401(self, task, comment):
        response = APIClient().get(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 401

    def test_unauthenticated_delete_returns_401(self, task, comment):
        response = APIClient().delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 401


@pytest.mark.django_db
class TestCommentRetrieve:
    def test_author_can_retrieve_comment(self, member, task, comment, auth_client):
        response = auth_client(member).get(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 200

    def test_response_contains_content(self, member, task, comment, auth_client):
        response = auth_client(member).get(task_comment_detail_url(task.pk, comment.pk))
        assert response.data['content'] == comment.content

    def test_nonexistent_comment_returns_404(self, member, task, auth_client):
        response = auth_client(member).get(task_comment_detail_url(task.pk, 99999))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCommentDelete:
    def test_author_can_delete_comment(self, member, task, comment, auth_client):
        response = auth_client(member).delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 204
        assert not TaskCommentsModel.objects.filter(pk=comment.pk).exists()

    def test_non_author_cannot_delete_comment(self, owner, task, comment, auth_client):
        response = auth_client(owner).delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 403
        assert TaskCommentsModel.objects.filter(pk=comment.pk).exists()

    def test_outsider_cannot_delete_comment(self, outsider, task, comment, auth_client):
        response = auth_client(outsider).delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code in (403, 404)
