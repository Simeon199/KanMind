from rest_framework import permissions

class IsAuthenticatedAndAssignee(permissions.BasePermission):
    """
    For GET /api/tasks/assigned-to-me/
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
class IsAuthenticatedAndReviewer(permissions.BasePermission):
    """
    For GET /api/tasks/reviewing/
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
class IsMemberOfBoard(permissions.BasePermission):
    """
    For POST, PATCH, GET comments
    """
    def has_permission(self, request, view):
        # For POST, get the board from the request data or URL
        board_id = request.data.get('board')
        if not board_id and hasattr(view, 'kwargs'):
            # Try to get board from the task if task_id is in the URL
            task_id = view.kwargs.get('pk') or view.kwargs.get('task_id')
            if task_id:
                from tasks_app.models import Task
                try:
                    board_id = Task.objects.get(pk=task_id).board_id
                except Task.DoesNotExist:
                    return False
                
        if not board_id:
            return False
        from board_app.models import Board
        try: 
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return False
        user = request.user
        return board.members.filter(id=user.id).exists() or board.owner == user
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(obj, 'board'):
            board = obj.board
        elif hasattr(obj, 'task') and hasattr(obj.task, 'board'):
            board = obj.task.board
        else:
            return False
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