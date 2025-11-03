from rest_framework import permissions

class OwnerOfBoardPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        # Only owner has the right to delete/update the board

        # user = request.user
        # if request.method in permissions.SAFE_METHODS:
        #     return obj.owner == user or obj.members.filter(id=user.id).exists()
        # return obj.owner == request.user
    
        # Relaxed permissions

        user = request.user
        is_owner = obj.owner == user
        is_member = obj.members.filter(id=user.id).exists()

        if request.method in permissions.SAFE_METHODS:
            return is_owner or is_member
        
        # allow members to update; only owner can delete
        if request.method in ('PUT', 'PATCH'):
            return is_owner or is_member
        
        if request.method == 'DELETE':
            return is_owner
        
        return is_owner