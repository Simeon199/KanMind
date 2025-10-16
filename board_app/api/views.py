from board_app.models import Board
from rest_framework import generics
from .serializers import BoardSerializer
from .permissions import OwnerOfBoardPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, BaseAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _


class TokenAdminAuthentication(TokenAuthentication):

    def authenticate(self, request):
        if not request.user.is_superuser:
            msg = _('User must be Admin!')
            raise exceptions.AuthenticationFailed(msg)
        return super().authenticate(request)
    

class BoardView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [] # Apply custom permission class here

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user) # Set owner to current user on creation
