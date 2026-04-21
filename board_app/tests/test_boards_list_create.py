import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from board_app.models import Board

BOARDS_URL = reverse('boards')


@pytest.mark.django_db
class TestBoardListAuthentication:
    def test_unauthenticated_returns_401(self):
        response = APIClient().get(BOARDS_URL)
        assert response.status_code == 401

    def test_authenticated_returns_200(self, owner, auth_client):
        response = auth_client(owner).get(BOARDS_URL)
        assert response.status_code == 200


@pytest.mark.django_db
class TestBoardListFiltering:
    def test_owner_sees_own_board(self, owner, board, auth_client):
        response = auth_client(owner).get(BOARDS_URL)
        ids = [b['id'] for b in response.data]
        assert board.id in ids

    def test_member_sees_board(self, member, board, auth_client):
        response = auth_client(member).get(BOARDS_URL)
        ids = [b['id'] for b in response.data]
        assert board.id in ids

    def test_outsider_cannot_see_board(self, outsider, board, auth_client):
        response = auth_client(outsider).get(BOARDS_URL)
        ids = [b['id'] for b in response.data]
        assert board.id not in ids

    def test_user_sees_only_own_boards(self, owner, outsider, auth_client):
        other_board = Board.objects.create(title='Other Board', owner=outsider)
        response = auth_client(owner).get(BOARDS_URL)
        ids = [b['id'] for b in response.data]
        assert other_board.id not in ids

    def test_returns_list(self, owner, board, auth_client):
        response = auth_client(owner).get(BOARDS_URL)
        assert isinstance(response.data, list)

    def test_no_duplicate_boards_when_owner_and_member(self, owner, board, auth_client):
        board.members.add(owner)
        response = auth_client(owner).get(BOARDS_URL)
        ids = [b['id'] for b in response.data]
        assert ids.count(board.id) == 1


@pytest.mark.django_db
class TestBoardCreate:
    def test_unauthenticated_returns_401(self):
        response = APIClient().post(BOARDS_URL, {'title': 'New'}, format='json')
        assert response.status_code == 401

    def test_creates_board_returns_201(self, owner, auth_client):
        response = auth_client(owner).post(BOARDS_URL, {'title': 'New Board'}, format='json')
        assert response.status_code == 201

    def test_owner_is_authenticated_user(self, owner, auth_client):
        auth_client(owner).post(BOARDS_URL, {'title': 'My Board'}, format='json')
        board = Board.objects.get(title='My Board')
        assert board.owner == owner

    def test_board_saved_in_db(self, owner, auth_client):
        auth_client(owner).post(BOARDS_URL, {'title': 'Saved Board'}, format='json')
        assert Board.objects.filter(title='Saved Board').exists()

    def test_response_contains_id_and_title(self, owner, auth_client):
        response = auth_client(owner).post(BOARDS_URL, {'title': 'My Board'}, format='json')
        assert 'id' in response.data
        assert response.data['title'] == 'My Board'

    def test_create_with_members(self, owner, member, auth_client):
        response = auth_client(owner).post(
            BOARDS_URL,
            {'title': 'Board With Members', 'members': [member.id]},
            format='json',
        )
        assert response.status_code == 201
        board = Board.objects.get(id=response.data['id'])
        assert board.members.filter(id=member.id).exists()

    def test_missing_title_returns_400(self, owner, auth_client):
        response = auth_client(owner).post(BOARDS_URL, {}, format='json')
        assert response.status_code == 400
