from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from .tasks import send_password_reset_email
from django.utils import timezone

from .models import Role, DeletionRequest, AuditLog
from .serializers import (
    UserListSerializer, UserCreateSerializer, UserProfileSerializer,
    ChangePasswordSerializer, AdminResetPasswordSerializer,
    RoleSerializer, DeletionRequestSerializer, AuditLogSerializer
)

User = get_user_model()


# ----------------------------
# Custom Permissions
# ----------------------------
class IsOwnerOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name in ['Owner', 'Manager']


class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or (request.user.role and request.user.role.name in ['Owner', 'Manager'])


# ----------------------------
# User ViewSet
# ----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['profile', 'update_profile']:
            return UserProfileSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'reset_password']:
            return [IsOwnerOrManager()]
        if self.action in ['change_password', 'profile', 'update_profile']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='profile/update')
    def update_profile(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = AdminResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Password reset successfully."})

    @action(detail=False, methods=['put'], url_path='change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": "Incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"detail": "Password changed successfully."})


# ----------------------------
# Role ViewSet
# ----------------------------
class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


# ----------------------------
# Deletion Request ViewSet
# ----------------------------
class DeletionRequestViewSet(viewsets.ModelViewSet):
    queryset = DeletionRequest.objects.all()
    serializer_class = DeletionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        req = self.get_object()
        if not request.user.role or request.user.role.name not in ['Owner', 'Manager']:
            return Response({"error": "Permission denied."}, status=403)

        req.is_approved = True
        req.reviewed_by = request.user
        req.reviewed_at = now()
        req.save()

        # Soft delete target object (if logic needed, implement per-module)
        return Response({"detail": "Deletion request approved."})


# ----------------------------
# Audit Log ViewSet
# ----------------------------
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]


# ----------------------------
# Password Reset API Views
# ----------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        otp = user.generate_otp()
        send_password_reset_email.delay(user.email, otp)
        return Response({"detail": "OTP sent to your email."})
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_and_reset_password(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')

    try:
        user = User.objects.get(email=email)
        if user.otp_code == otp and user.otp_expiry > timezone.now():
            user.set_password(new_password)
            user.otp_code = None
            user.otp_expiry = None
            user.save()
            return Response({"detail": "Password reset successful."})
        return Response({"error": "Invalid or expired OTP."}, status=400)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)
