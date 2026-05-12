from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    FARMER          = "FARMER",          "Farmer"
    CELL_LEADER     = "CELL_LEADER",     "Cell Leader"
    VETERINARIAN    = "VETERINARIAN",    "Veterinarian"
    DISTRICT_LEADER = "DISTRICT_LEADER", "District Leader"
    ADMIN           = "ADMIN",           "Admin"


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username     = models.CharField(max_length=50, unique=True)
    email        = models.EmailField(unique=True, null=True, blank=True)
    full_name    = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    role         = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.FARMER)
    district     = models.ForeignKey("districts.District", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    national_id  = models.CharField(max_length=16, null=True, blank=True)
    is_active    = models.BooleanField(default=True)
    is_verified  = models.BooleanField(default=False)
    is_staff     = models.BooleanField(default=False)
    last_login   = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]
    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["role"]), models.Index(fields=["district"])]

    def __str__(self): return f"{self.full_name} ({self.role})"

    @property
    def is_farmer(self): return self.role == UserRole.FARMER
    @property
    def is_cell_leader(self): return self.role == UserRole.CELL_LEADER
    @property
    def is_veterinarian(self): return self.role == UserRole.VETERINARIAN
    @property
    def is_district_leader(self): return self.role == UserRole.DISTRICT_LEADER
    @property
    def is_admin_role(self): return self.role == UserRole.ADMIN


class AuditLog(models.Model):
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_logs")
    action        = models.CharField(max_length=20)
    resource_type = models.CharField(max_length=50)
    resource_id   = models.BigIntegerField(null=True, blank=True)
    old_values    = models.JSONField(null=True, blank=True)
    new_values    = models.JSONField(null=True, blank=True)
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    user_agent    = models.TextField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user"]), models.Index(fields=["created_at"])]


class OTPCode(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_codes")
    code       = models.CharField(max_length=6)
    is_used    = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_codes"
