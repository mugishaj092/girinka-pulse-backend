"""Role-based permission classes."""
from rest_framework.permissions import BasePermission


class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "FARMER")


class IsCellLeader(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "CELL_LEADER")


class IsVeterinarian(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "VETERINARIAN")


class IsDistrictLeader(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "DISTRICT_LEADER")


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMIN")


class IsCellLeaderOrAbove(BasePermission):
    ALLOWED = {"CELL_LEADER", "VETERINARIAN", "DISTRICT_LEADER", "ADMIN"}
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.ALLOWED)


class IsVetOrAbove(BasePermission):
    ALLOWED = {"VETERINARIAN", "DISTRICT_LEADER", "ADMIN"}
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.ALLOWED)


class IsDistrictLeaderOrAdmin(BasePermission):
    ALLOWED = {"DISTRICT_LEADER", "ADMIN"}
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.ALLOWED)


class IsSameDistrict(BasePermission):
    """Allow if user is in the same district as the object, or is Admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True
        obj_district = getattr(obj, "district_id", None) or getattr(getattr(obj, "district", None), "id", None)
        return obj_district == request.user.district_id


# Re-export DRF's IsAuthenticated for convenience
from rest_framework.permissions import IsAuthenticated  # noqa
