from rest_framework import permissions

class OwnerOfBoardPermission(permissions.BasePermission):
    """
    Permission class for board-related operations.
    Ensures users have appropriate permissions based on their role (owner or member)
    and the HTTP method being used
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission for the specific board object based on the request method.

        For safe methods (GET, HEAD, OPTIONS), both owners and members are allowed.
        For PATCH, both owners and members can update.
        For PUT and DELETE, only the owner is allowed.
        For any other method, only the owner is allowed by default.

        Args:
           request: The HTTP request object.
           view: The view being accessed.
           obj: The board object being accessed.

        Returns:
           bool: True if the user has permission, False otherwise.
        """
        
        user = request.user
        is_owner = obj.owner == user
        is_member = obj.members.filter(id=user.id).exists()
        if request.method in permissions.SAFE_METHODS:
            return is_owner or is_member
        if request.method == 'PATCH':
            return is_owner or is_member
        if request.method == 'PUT':
            return is_owner 
        if request.method == 'DELETE':
            return is_owner
        return is_owner