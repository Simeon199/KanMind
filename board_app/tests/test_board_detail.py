import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from board_app.models import Board


def detail_url(pk):
    return reverse('board-detail', kwargs={'pk': pk})


@pytest.mark.django_db
class TestBoardDetailAuthentication:
    def test_unauthenticated_get_returns_401(self, board):
        response = APIClient().get(detail_url(board.pk))
        assert response.status_code == 401

    def test_unauthenticated_patch_returns_401(self, board):
        response = APIClient().patch(detail_url(board.pk), {'title': 'X'}, format='json')
        assert response.status_code == 401

    def test_unauthenticated_delete_returns_401(self, board):
        response = APIClient().delete(detail_url(board.pk))
        assert response.status_code == 401


@pytest.mark.django_db
class TestBoardDetailGet:
    def test_owner_can_retrieve(self, owner, board, auth_client):
        response = auth_client(owner).get(detail_url(board.pk))
        assert response.status_code == 200

    def test_member_can_retrieve(self, member, board, auth_client):
        response = auth_client(member).get(detail_url(board.pk))
        assert response.status_code == 200

    def test_outsider_gets_403(self, outsider, board, auth_client):
        response = auth_client(outsider).get(detail_url(board.pk))
        assert response.status_code == 403

    def test_nonexistent_board_returns_404(self, owner, auth_client):
        response = auth_client(owner).get(detail_url(99999))
        assert response.status_code == 404

    def test_response_contains_expected_fields(self, owner, board, auth_client):
        response = auth_client(owner).get(detail_url(board.pk))
        for field in ('id', 'title', 'owner_id', 'members', 'tasks'):
            assert field in response.data

    def test_response_title_matches(self, owner, board, auth_client):
        response = auth_client(owner).get(detail_url(board.pk))
        assert response.data['title'] == board.title

    def test_response_owner_id_matches(self, owner, board, auth_client):
        response = auth_client(owner).get(detail_url(board.pk))
        assert response.data['owner_id'] == owner.id

    def test_members_list_contains_member(self, owner, member, board, auth_client):
        response = auth_client(owner).get(detail_url(board.pk))
        member_ids = [m['id'] for m in response.data['members']]
        assert member.id in member_ids


@pytest.mark.django_db
class TestBoardDetailPatch:
    def test_owner_can_patch_title(self, owner, board, auth_client):
        response = auth_client(owner).patch(detail_url(board.pk), {'title': 'Updated'}, format='json')
        assert response.status_code == 200
        board.refresh_from_db()
        assert board.title == 'Updated'

    def test_member_can_patch(self, member, board, auth_client):
        response = auth_client(member).patch(detail_url(board.pk), {'title': 'By Member'}, format='json')
        assert response.status_code == 200

    def test_outsider_cannot_patch(self, outsider, board, auth_client):
        response = auth_client(outsider).patch(detail_url(board.pk), {'title': 'Hack'}, format='json')
        assert response.status_code == 403

    def test_patch_updates_members(self, owner, outsider, board, auth_client):
        response = auth_client(owner).patch(
            detail_url(board.pk),
            {'members': [outsider.id]},
            format='json',
        )
        assert response.status_code == 200
        board.refresh_from_db()
        assert board.members.filter(id=outsider.id).exists()

    def test_patch_response_excludes_members_write_field(self, owner, board, auth_client):
        response = auth_client(owner).patch(detail_url(board.pk), {'title': 'X'}, format='json')
        assert 'members' not in response.data


@pytest.mark.django_db
class TestBoardDetailDelete:
    def test_owner_can_delete(self, owner, board, auth_client):
        response = auth_client(owner).delete(detail_url(board.pk))
        assert response.status_code == 204
        assert not Board.objects.filter(pk=board.pk).exists()

    def test_member_cannot_delete(self, member, board, auth_client):
        response = auth_client(member).delete(detail_url(board.pk))
        assert response.status_code == 403
        assert Board.objects.filter(pk=board.pk).exists()

    def test_outsider_cannot_delete(self, outsider, board, auth_client):
        response = auth_client(outsider).delete(detail_url(board.pk))
        assert response.status_code == 403
