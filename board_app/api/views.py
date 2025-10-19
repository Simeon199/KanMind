from board_app.models import Board
from rest_framework import generics
from .serializers import BoardSerializer
from .permissions import OwnerOfBoardPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext_lazy as _

# class TokenOwnerAuthentication(TokenAuthentication):

#     def authenticate(self, request):
#         if not request.user.is_superuser:
#             msg = _('User must be Admin!')
#             raise exceptions.AuthenticationFailed(msg)
#         return super().authenticate(request)

class BoardView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated] # OwnerOfBoardPermission

    # def get_queryset(self):
    #     user = self.request.user
    #     return Board.objects.filter(owner=user) | Board.objects.filter(members=user)
    
    # def perform_create(self, serializer):
    #     return serializer.save(owner=self.request.user)


# class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Board.objects.all()
#     serializer_class = BoardSerializer
#     permission_classes = [IsAuthenticated, OwnerOfBoardPermission] 

#     def perform_update(self, serializer):
#         serializer.save(owner=self.request.user) 
