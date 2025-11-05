from rest_framework import permissions

class OwnerOfBoardPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        user = request.user
        is_owner = obj.owner == user
        is_member = obj.members.filter(id=user.id).exists()

        if request.method in permissions.SAFE_METHODS:
            return is_owner or is_member
        
        # PATCH: owner or member can update members
        if request.method == 'PATCH':
            return is_owner or is_member
        
        # PUT: only owner can fully update:
        if request.method == 'PUT':
            return is_owner 
        
        # DELETE: only owner can delete
        if request.method == 'DELETE':
            return is_owner
        
        # Default: only owner
        return is_owner