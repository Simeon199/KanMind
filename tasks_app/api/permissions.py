from rest_framework import permissions
from tasks_app.models import Task
from board_app.models import Board

class IsAuthenticatedAndAssignee(permissions.BasePermission):
    """
    For GET /api/tasks/assigned-to-me/
    Ensures the user is authenticated.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
class IsAuthenticatedAndReviewer(permissions.BasePermission):
    """
    Permission for GET /api/tasks/reviewing/.
    Ensures the user is authenticated.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsMemberOfBoard(permissions.BasePermission):
    """
    Permission for POST, PATCH, and GET comments.
    Ensures the user is a member of the board or the board owner.
    """
    def has_permission(self, request, view):
        board = self._get_board_from_request(request, view)
        if not board:
            return False
        return self._is_board_member_or_owner(request.user, board)
    
    def has_object_permission(self, request, view, obj):
        board = self._get_board_from_object(obj)
        if not board:
            return False
        return self._is_board_member_or_owner(request.user, board)
    
    def _get_board_from_request(self, request, view):
        """
        Retrieve the board from the request data or the task in the URL.
        """
        board_id = request.data.get('board')
        if not board_id and hasattr(view, 'kwargs'):
            task_id = view.kwargs.get('pk') or view.kwargs.get('task_id')
            if task_id:
                try:
                    return Task.objects.get(pk=task_id).board
                except Task.DoesNotExist:
                    return None
            if board_id:
                try:
                    return Board.objects.get(pk=board_id)
                except Board.DoesNotExist:
                    return None
            return None
        
    def _get_board_from_object(self, obj):
        """
        Retrieve the board from the object (task or comment).
        """
        if hasattr(obj, 'board'):
            return obj.board
        if hasattr(obj, 'task') and hasattr(obj.task, 'board'):
            return obj.task.board
        return None
    
    def _is_board_member_or_owner(self, user, board):
        """
        Check if the user is a member of the board or the board owner.
        """
        return board.members.filter(id=user.id).exists() or board.owner == user
    
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