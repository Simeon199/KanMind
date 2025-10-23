from board_app.models import Board
from rest_framework import generics
from .serializers import BoardSerializer
from .permissions import OwnerOfBoardPermission
from rest_framework.permissions import IsAuthenticated

class BoardView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, OwnerOfBoardPermission] 

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)