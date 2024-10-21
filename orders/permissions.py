from rest_framework import permissions


class IsOwnerOfOrder(permissions.BasePermission):
    """
    مجوزی که اجازه دسترسی به سفارشات را فقط به صاحب آن می‌دهد.
    """
    def has_object_permission(self, request, view, obj):

        return request.user.is_authenticated and obj.user == request.user
