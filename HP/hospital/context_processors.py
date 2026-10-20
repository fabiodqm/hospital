from django.conf import settings

from .module_registry import NAVIGATION
from .permissions import can_access_module, can_manage_admin, can_manage_roles


def hospital_context(request):
    nav = []
    if hasattr(request, 'user') and request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        role = getattr(profile, 'role', '') if profile else ''
        for slug, label, icon in NAVIGATION:
            # O portal do paciente aparece no menu lateral somente para conta de paciente.
            # Equipe interna continua usando os módulos clínicos normais.
            if slug == 'portal-paciente' and role != 'paciente':
                continue
            if can_access_module(request.user, slug):
                nav.append({'slug': slug, 'label': label, 'icon': icon})
    return {
        'hospital_name': settings.HOSPITAL_NAME,
        'hospital_primary_color': settings.HOSPITAL_PRIMARY_COLOR,
        'nav_modules': nav,
        'can_open_admin_panel': (
            hasattr(request, 'user')
            and request.user.is_authenticated
            and (can_manage_admin(request.user) or can_manage_roles(request.user))
        ),
    }
