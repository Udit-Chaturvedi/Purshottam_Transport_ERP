from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, DeletionRequest, AuditLog
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

User = get_user_model()


# ----------------------------
# Role Serializer
# ----------------------------
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'can_delete']


# ----------------------------
# User List Serializer (Admin View)
# ----------------------------
class UserListSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True, source='role')

    class Meta:
        model = User
        fields = ['id', 'employee_id', 'username', 'full_name', 'email', 'phone', 'role', 'role_id', 'is_active', 'is_deleted']


# ----------------------------
# User Create Serializer
# ----------------------------
class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone', 'password', 'role_id']

    def create(self, validated_data):
        role = validated_data.pop('role_id')
        user = User.objects.create_user(**validated_data)
        user.role = role
        user.save()
        return user


# ----------------------------
# Profile Serializer (for self view/edit)
# ----------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'employee_id', 'username', 'full_name', 'email', 'phone', 'role']


# ----------------------------
# Change Password Serializer
# ----------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


# ----------------------------
# Reset Password (Admin-triggered)
# ----------------------------
class AdminResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password])


# ----------------------------
# Deletion Request Serializer
# ----------------------------
class DeletionRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DeletionRequest
        fields = [
            'id', 'module', 'object_id', 'reason',
            'requested_by', 'is_approved',
            'reviewed_by', 'reviewed_at', 'created_at'
        ]


# ----------------------------
# Audit Log Serializer
# ----------------------------
class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'model_name', 'object_id', 'timestamp', 'change_description']
