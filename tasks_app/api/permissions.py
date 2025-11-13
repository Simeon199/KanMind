from rest_framework import permissions
from django.db import models
from tasks_app.models import Task
from board_app.models import Board

import logging

logger = logging.getLogger(__name__)

class IsAuthenticatedAndAssignee(permissions.BasePermission):
    """
    For GET /api/tasks/assigned-to-me/
    Ensures the user is authenticated and is an assignee on boards they are a member of.
    """
    def has_permission(self, request, view):
        if not(request.user and request.user.is_authenticated):
            return False
    
class IsAuthenticatedAndReviewer(permissions.BasePermission):
    """
    For GET /api/tasks/reviewing/
    Ensures the user is authenticated and is a reviewer on boards they are member of.
    """
    def has_permission(self, request, view):
        if not(request.user and request.user.is_authenticated):
            return False
    
class IsAuthenticatedAndReviewer(permissions.BasePermission):
    """
    Permission for GET /api/tasks/reviewing/.
    Ensures the user is authenticated.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsMemberOfBoard(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            logger.debug(f"SAFE_METHODS check: User {request.user} is authenticated: {request.user.is_authenticated}")
            return bool(request.user and request.user.is_authenticated)

        # Existing logic for non-safe methods
        board = None
        data = getattr(request, "data", {}) or {}

        # Try to get the board from the request data or task ID
        board_id = data.get("board") or data.get("board_id") or data.get("boardId")
        if board_id:
            try:
                board = Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                return False

        if not board:
            task_id = view.kwargs.get("pk") or view.kwargs.get("task_id")
            if task_id:
                try:
                    board = Task.objects.get(pk=task_id).board
                except Task.DoesNotExist:
                    return False

        if not board:
            return False

        return board.members.filter(id=request.user.id).exists() or board.owner_id == request.user.id
    
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