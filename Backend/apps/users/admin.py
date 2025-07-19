from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, DeletionRequest, AuditLog


# ----------------------------
# Inline Filters for Role
# ----------------------------
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'can_delete']
    search_fields = ['name']
    ordering = ['name']


# ----------------------------
# Custom User Admin
# ----------------------------
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('employee_id', 'username', 'full_name', 'email', 'role', 'is_active', 'is_deleted', 'is_staff')
    list_filter = ('role', 'is_active', 'is_deleted', 'is_staff')
    search_fields = ('username', 'full_name', 'employee_id', 'email')
    ordering = ('id',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'phone')}),
        ('Role & Access', {'fields': ('employee_id', 'role', 'is_active', 'is_deleted', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'email', 'password1', 'password2', 'role')}
        ),
    )


# ----------------------------
# Deletion Request Admin
# ----------------------------
@admin.register(DeletionRequest)
class DeletionRequestAdmin(admin.ModelAdmin):
    list_display = ('module', 'object_id', 'requested_by', 'reason', 'is_approved', 'reviewed_by', 'created_at')
    list_filter = ('module', 'is_approved', 'created_at')
    search_fields = ('object_id', 'reason', 'requested_by__username', 'reviewed_by__username')


# ----------------------------
# Audit Log Admin
# -------------
