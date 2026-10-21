from rest_framework import permissions
0
class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsInstructorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):

        # GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # POST, PUT, PATCH, DELETE
        return bool(
            request.user \
            and request.user.is_authenticated \
            and (request.user.is_staff or request.user.role == "INSTRUCTOR")
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return obj.instructor == request.user


class IsAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user