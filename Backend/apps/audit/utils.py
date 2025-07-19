from .models import AuditLog
from django.utils.timezone import now

def log_audit_action(user, action, instance):
    model_name = instance.__class__.__name__
    object_id = instance.pk
    change_description = f"{action} {model_name} (ID: {object_id})"

    AuditLog.objects.create(
        user=user,
        action=action,
        model=model_name,
        object_id=object_id,
        change_description=change_description,
        timestamp=now()
    )
