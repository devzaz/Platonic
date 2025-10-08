from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCreateOrStaffRead(BasePermission):
    """Allow anyone to create; only staff can list/retrieve/update/delete."""
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return bool(request.user and request.user.is_staff)