from board_app.models import Board
from rest_framework import generics
from .serializers import BoardSerializer, SingleBoardSerializer
from .permissions import OwnerOfBoardPermission
from rest_framework.permissions import IsAuthenticated

class BoardView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

class SingleBoardView(generics.RetrieveAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
        
    def get_queryset(self):
        board_id = self.kwargs.get('pk')
        return Board.objects.filter(id=board_id)

class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    
    # BoardRetrieveUpdateDestroyView already supports the PATCH and DELETE requests because it inherits from RetrieveUpdateDestroyAPIView
    
    queryset = Board.objects.all()
    serializer_class = SingleBoardSerializer
    permission_classes = [IsAuthenticated, OwnerOfBoardPermission] 

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)