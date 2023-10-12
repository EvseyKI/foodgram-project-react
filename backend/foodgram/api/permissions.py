from rest_framework.permissions import BasePermission


class CheckPermissionsToUpdateAndDelete(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('PATCH', 'DELETE'):
            return bool(request.user == obj.author)
        return True