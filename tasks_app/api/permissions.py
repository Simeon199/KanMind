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
    For POST, PATCH, GET comments, POST comments
    """
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