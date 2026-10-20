from django.contrib import messages
from django.db import DatabaseError, OperationalError, ProgrammingError

from .models import AuditLog


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def audit(request, action, module='', obj=None, before=None, after=None, message=''):
    try:
        AuditLog.objects.create(
            user=request.user if request and request.user.is_authenticated else None,
            action=action,
            module=module,
            object_label=str(obj)[:180] if obj else '',
            object_id=str(getattr(obj, 'pk', '') or ''),
            before=before or {},
            after=after or {},
            ip_address=get_client_ip(request) if request else None,
            message=message,
        )
    except Exception:
        pass


def safe_queryset(request, qs, fallback=None, public_message='Não foi possível carregar os dados agora.'):
    try:
        return list(qs)
    except (ProgrammingError, OperationalError, DatabaseError) as exc:
        audit(request, 'error', message=str(exc))
        if request:
            messages.error(request, public_message)
        return fallback if fallback is not None else []


def safe_count(request, model, default=0):
    try:
        return model.objects.count()
    except (ProgrammingError, OperationalError, DatabaseError) as exc:
        audit(request, 'error', module=model.__name__, message=str(exc))
        return default


def safe_save_form(request, form, module=''):
    try:
        obj = form.save()
        audit(request, 'create', module=module, obj=obj)
        return obj, None
    except (ProgrammingError, OperationalError, DatabaseError) as exc:
        audit(request, 'error', module=module, message=str(exc))
        return None, 'Não foi possível salvar. Verifique se as tabelas do banco ja foram migradas.'
