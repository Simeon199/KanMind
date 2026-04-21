"""
Tests for task comment endpoints.

Endpoints:
- GET/POST /api/tasks/<pk>/comments/
- GET/DELETE /api/tasks/<task_id>/comments/<pk>/

Covers:
- Authentication: all methods require a valid token.
- Comment list: board members and owners can list comments; outsiders are blocked;
  existing comments appear in the list; the response shape is verified.
- Comment create: members and owners can add comments; the author is set to the
  authenticated user; the comment is linked to the correct task; empty or missing
  content is rejected with HTTP 400.
- Comment detail GET: the comment author can retrieve a comment; non-existent
  comment IDs return HTTP 404.
- Comment delete: the author can delete their own comment; non-authors receive
  HTTP 403; the record is removed from the database on success.
"""

import pytest
from rest_framework.test import APIClient
from tasks_app.models import TaskCommentsModel
from .conftest import task_comments_url, task_comment_detail_url


@pytest.mark.django_db
class TestCommentListAuthentication:
    """
    Tests that unauthenticated access to the comment list endpoint is rejected.
    """

    def test_unauthenticated_get_returns_401(self, task):
        """
        An unauthenticated GET request for comments is rejected with HTTP 401.
        """
        response = APIClient().get(task_comments_url(task.pk))
        assert response.status_code == 401

    def test_unauthenticated_post_returns_401(self, task):
        """
        An unauthenticated POST request to add a comment is rejected with HTTP 401.
        """
        response = APIClient().post(task_comments_url(task.pk), {'content': 'x'}, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestCommentList:
    """
    Tests for GET /api/tasks/<pk>/comments/.
    """

    def test_member_can_list_comments(self, member, task, comment, auth_client):
        """
        A board member can list comments for a task and receives HTTP 200 OK.
        """
        response = auth_client(member).get(task_comments_url(task.pk))
        assert response.status_code == 200

    def test_owner_can_list_comments(self, owner, task, comment, auth_client):
        """
        The board owner can list comments for a task and receives HTTP 200 OK.
        """
        response = auth_client(owner).get(task_comments_url(task.pk))
        assert response.status_code == 200

    def test_outsider_cannot_list_comments(self, outsider, task, comment, auth_client):
        """
        A user with no board membership cannot list comments for the task.
        """
        response = auth_client(outsider).get(task_comments_url(task.pk))
        assert response.status_code in (403, 404)

    def test_returns_existing_comment(self, member, task, comment, auth_client):
        """
        An existing comment appears in the list response by its ID.
        """
        response = auth_client(member).get(task_comments_url(task.pk))
        ids = [c['id'] for c in response.data]
        assert comment.id in ids

    def test_response_contains_expected_fields(self, member, task, comment, auth_client):
        """
        Each comment object in the list response contains id, content, author, and created_at.
        """
        response = auth_client(member).get(task_comments_url(task.pk))
        first = response.data[0]
        for field in ('id', 'content', 'author', 'created_at'):
            assert field in first


@pytest.mark.django_db
class TestCommentCreate:
    """
    Tests for POST /api/tasks/<pk>/comments/.
    """

    def test_member_can_add_comment(self, member, task, auth_client):
        """
        A board member can add a comment to a task and receives HTTP 201 Created.
        """
        response = auth_client(member).post(
            task_comments_url(task.pk), {'content': 'New comment'}, format='json'
        )
        assert response.status_code == 201

    def test_owner_can_add_comment(self, owner, task, auth_client):
        """
        The board owner can add a comment to a task and receives HTTP 201 Created.
        """
        response = auth_client(owner).post(
            task_comments_url(task.pk), {'content': 'Owner comment'}, format='json'
        )
        assert response.status_code == 201

    def test_outsider_cannot_add_comment(self, outsider, task, auth_client):
        """
        A user with no board membership cannot add a comment to the task.
        """
        response = auth_client(outsider).post(
            task_comments_url(task.pk), {'content': 'Hack'}, format='json'
        )
        assert response.status_code in (403, 404)

    def test_author_set_to_authenticated_user(self, member, task, auth_client):
        """
        The comment's author is automatically set to the authenticated user.
        """
        auth_client(member).post(
            task_comments_url(task.pk), {'content': 'Mine'}, format='json'
        )
        c = TaskCommentsModel.objects.get(content='Mine')
        assert c.author == member

    def test_comment_linked_to_correct_task(self, member, task, auth_client):
        """
        The newly created comment is linked to the task specified in the URL.
        """
        auth_client(member).post(
            task_comments_url(task.pk), {'content': 'Linked'}, format='json'
        )
        c = TaskCommentsModel.objects.get(content='Linked')
        assert c.task == task

    def test_empty_content_returns_400(self, member, task, auth_client):
        """
        A POST request with an empty 'content' value is rejected with HTTP 400.
        """
        response = auth_client(member).post(
            task_comments_url(task.pk), {'content': ''}, format='json'
        )
        assert response.status_code == 400

    def test_missing_content_returns_400(self, member, task, auth_client):
        """
        A POST request without a 'content' field is rejected with HTTP 400.
        """
        response = auth_client(member).post(
            task_comments_url(task.pk), {}, format='json'
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestCommentDetailAuthentication:
    """
    Tests that unauthenticated access to the comment detail endpoint is rejected.
    """

    def test_unauthenticated_get_returns_401(self, task, comment):
        """
        An unauthenticated GET request for a comment detail is rejected with HTTP 401.
        """
        response = APIClient().get(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 401

    def test_unauthenticated_delete_returns_401(self, task, comment):
        """
        An unauthenticated DELETE request for a comment is rejected with HTTP 401.
        """
        response = APIClient().delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 401


@pytest.mark.django_db
class TestCommentRetrieve:
    """
    Tests for GET /api/tasks/<task_id>/comments/<pk>/.
    """

    def test_author_can_retrieve_comment(self, member, task, comment, auth_client):
        """
        The comment author can retrieve the comment detail and receives HTTP 200 OK.
        """
        response = auth_client(member).get(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 200

    def test_response_contains_content(self, member, task, comment, auth_client):
        """
        The 'content' field in the response matches the comment's actual content.
        """
        response = auth_client(member).get(task_comment_detail_url(task.pk, comment.pk))
        assert response.data['content'] == comment.content

    def test_nonexistent_comment_returns_404(self, member, task, auth_client):
        """
        Requesting a comment with a non-existent ID returns HTTP 404 Not Found.
        """
        response = auth_client(member).get(task_comment_detail_url(task.pk, 99999))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCommentDelete:
    """
    Tests for DELETE /api/tasks/<task_id>/comments/<pk>/.
    """

    def test_author_can_delete_comment(self, member, task, comment, auth_client):
        """
        The comment author can delete their comment; the record is removed from the database.
        """
        response = auth_client(member).delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 204
        assert not TaskCommentsModel.objects.filter(pk=comment.pk).exists()

    def test_non_author_cannot_delete_comment(self, owner, task, comment, auth_client):
        """
        A user who is not the comment author receives HTTP 403 when attempting to delete it.
        """
        response = auth_client(owner).delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code == 403
        assert TaskCommentsModel.objects.filter(pk=comment.pk).exists()

    def test_outsider_cannot_delete_comment(self, outsider, task, comment, auth_client):
        """
        A user with no board membership cannot delete a comment on the task.
        """
        response = auth_client(outsider).delete(task_comment_detail_url(task.pk, comment.pk))
        assert response.status_code in (403, 404)
