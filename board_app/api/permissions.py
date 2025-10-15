from rest_framework import permissions

class OwnerOfBoardPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Get the current user from the request
        user = request.user
        
        # Check if the user is an owner of the board
        return obj.owner == user