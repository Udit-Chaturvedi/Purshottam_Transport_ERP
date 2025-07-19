from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, RoleViewSet, DeletionRequestViewSet, AuditLogViewSet, request_password_reset, verify_otp_and_reset_password
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'deletion-requests', DeletionRequestViewSet, basename='deletionrequest')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('password-reset/request/', request_password_reset, name='password_reset_request'),
    path('password-reset/verify/', verify_otp_and_reset_password, name='password_reset_verify'),
]

