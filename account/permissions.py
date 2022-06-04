from rest_framework.permissions import BasePermission

class IsOwnerOnly(BasePermission):
    

    def has_object_permission(self, request, view, obj):

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user or request.user.is_staff