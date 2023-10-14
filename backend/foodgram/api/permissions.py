from rest_framework.permissions import BasePermission


class IsAuthorPermissions(BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        author = obj.author
        return user == author or request.method not in ('PATCH', 'DELETE')
