from board_app.models import Board
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import BoardSerializer, SingleBoardSerializer, BoardUpdateSerializer
from .permissions import OwnerOfBoardPermission
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

class BoardView(generics.ListCreateAPIView):
    """
    API view for listing and creating boards.
    Lists boards where the user is the owner or a member.
    Creates new boards with the authenticated user as the owner.
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return a queryset of boards where the user is the owner or a member.

        Returns:
             Queryset: Filtered boards for the authenticated user.
        """
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()
    
    def perform_create(self, serializer):
        """
        Save the serializer with the authenticated user as the owner.
        
        Args: 
           serializer: The BoardSerializer instance.
        """
        serializer.save(owner=self.request.user)

class BoardRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual boards.
    Requires the user to be authenticated and have appropriate permissions
    (e.g., owner or member based on the operation).
    """    
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, OwnerOfBoardPermission]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SingleBoardSerializer # Includes tasks
        elif self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return SingleBoardSerializer # Exludes tasks uses owner_data/members_data

class EmailCheckView(APIView):
    """
    API view for checking if a user exists by email.
    Returns user details if found, or an error if not.
    Requires the user to be authenticated.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET requests to check for a user by email.

        Query Parameters:
            email (str): The email address to search for.

        Returns: 
            Response: User details if found, or an error message.
        """
        email = request.query_params.get('email')
        if not email:
            return Response({'detail': 'Email is required as a query parameter'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            fullname = f"{user.first_name}{user.last_name}".strip() or user.username
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': fullname
            })
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)