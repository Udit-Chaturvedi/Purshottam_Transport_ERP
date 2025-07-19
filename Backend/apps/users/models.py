from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.crypto import get_random_string
import datetime


# ----------------------------
# Custom User Manager
# ----------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        username = username.strip()
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


# ----------------------------
# Role Model
# ----------------------------
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    can_delete = models.BooleanField(default=False)  # Flag to allow deletion rights

    def __str__(self):
        return self.name


# ----------------------------
# Custom User Model
# ----------------------------
class User(AbstractUser):
    employee_id = models.CharField(max_length=10, unique=True, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='users')

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last_user = User.objects.order_by('-id').first()
            last_id = int(last_user.employee_id.replace('PT', '')) if last_user and last_user.employee_id else 0
            self.employee_id = f"PT{last_id + 1}"
        super().save(*args, **kwargs)

    def generate_otp(self):
        """
        Generates a 6-digit OTP and sets the expiry time for 10 minutes from now.
        """
        self.otp_code = get_random_string(6, allowed_chars='1234567890')
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save()
        return self.otp_code

    def __str__(self):
        return f"{self.full_name} ({self.username})"


# ----------------------------
# Deletion Request Model
# ----------------------------
class DeletionRequest(models.Model):
    MODULE_CHOICES = [
        ('challan', 'Challan'),
        ('vehicle', 'Vehicle'),
        ('driver', 'Driver'),
        ('other', 'Other'),
    ]

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deletion_requests')
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    object_id = models.CharField(max_length=100)
    reason = models.TextField()
    is_approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_deletions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.requested_by} for {self.module} {self.object_id}"


# ----------------------------
# Audit Log Model
# ----------------------------
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    change_description = models.TextField()

    def __str__(self):
        return f"{self.action} on {self.model_name}({self.object_id}) by {self.user}"
