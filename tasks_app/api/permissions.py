from rest_framework import permissions
from django.db import models
from tasks_app.models import Task
from board_app.models import Board

class IsAuthenticatedAndRelatedToTask(permissions.BasePermission):
    """
    Base permission class to ensure the user is authenticated and related to tasks (as assignee or reviewer) on boards they are member of.
    
    Subclasses must define the 'role' attribute (e.g., 'assignee' or 'reviewer')
    """
    role = None

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and has tasks in the specified role on their boards.

        Args:
            request: The HTTP request object.
            view: The view being accessed.

        Returns:
            bool: True if the user is authenticated and has related tasks, False otherwise.

        Raises: 
            ValueError: If the 'role' attribute is not defined in the subclass.
        """
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not self.role:
            raise ValueError("Role must be defined in the subclass.")
        
        user_boards = Board.objects.filter(members=request.user)
        filter_kwargs = {f"{self.role}": request.user, "board__in": user_boards}
        return Task.objects.filter(**filter_kwargs).exists()
    
class IsMemberOfBoard(permissions.BasePermission):
    """
    Permission class to ensure the user is a member of the board or the board owner.
    Allow safe methods (e.g., GET) for authenticated users and checks board membership for unsafe methods.
    """

    def has_permission(self, request, view):
        """
        Check permission for the request, allowing safe methods for authenticated users and verifying board 
        membership for unsafe methods.

        Args:
           request: The HTTP request object.
           view: The view being accessed.

        Returns:
           bool: True if the user has permission, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        board = self._get_board_from_request(request, view)
        if not board:
            return False
        return self._is_board_member_or_owner(request.user, board)
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permission to ensure the user is a member of the board or the board owner.

        Args: 
           request: The HTTP reuqest object.
           view: The view being accessed.
           obj: The object (Task or TaskCommentsModel) being accessed.
        
        Returns:
           bool: True if the user has permission for the object, False otherwise.
        """
        board = self._get_board_from_object(obj)
        if not board:
            return False
        return self._is_board_member_or_owner(request.user, board)
    
    def _get_board_from_request(self, request, view):
        """
        Retrieve the board from the request data or URL parameters.

        Args:
           request: The HTTP request object
           view: The view being accessed.

        Returns: 
           Board or None: The board instance if found, None otherwise.
        """
        data = getattr(request, "data", {}) or {}
        board_id = data.get("board") or data.get("board_id") or data.get("boardId")
        if board_id:
            try:
                return Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                return None
        
        task_id = view.kwargs.get("pk") or view.kwargs.get("task_id")
        if task_id:
            try:
                return Task.objects.get(pk=task_id).board
            except Task.DoesNotExist:
                return None
        return None
    
    def _get_board_from_object(self, obj):
        """
        Retrieve the board from the object (Task or TaskCommentsModel).

        Args:
           obj: The object being accessed.

        Returns:
           Board or None: The board instance if found, None otherwise.
        """
        if hasattr(obj, 'board'):
            return obj.board
        if hasattr(obj, 'task') and hasattr(obj.task, 'board'):
            return obj.task.board
        return None
    
    def _is_board_member_or_owner(self, user, board):
        """
        Check if the user is a member of the board or the board owner.
        
        Args: 
           user: The user to check.
           board: The board to check against.

        Returns:
           bool: True if the user is a member or owner, False otherwise.
        """

        return board.members.filter(id=user.id).exists() or board.owner_id == user.id
        
# Subclasses for specific roles

class IsAuthenticatedAndAssignee(IsAuthenticatedAndRelatedToTask):
    role = "assignee"

class IsAuthenticatedAndReviewer(IsAuthenticatedAndRelatedToTask):
    role = "reviewer"
    
class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    For DELETE /api/tasks/{task_id}
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.author == user or obj.board.owner == user
    
class IsCommentAuthor(permissions.BasePermission):
    """
    For DELETE /api/tasks/{task_id}/comments/{comment_id}/
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user