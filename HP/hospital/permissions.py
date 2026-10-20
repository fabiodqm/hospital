from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

ADMIN_ROLES = {'super_admin', 'admin', 'presidente_hospital'}
DIRECTION_ROLES = {
    'diretor', 'vice_diretor', 'diretor_clinico', 'diretor_medico',
    'diretor_administrativo', 'diretor_enfermagem'
}
SECTOR_CHIEF_ROLES = {
    'chefe_emergencia', 'chefe_uti', 'chefe_centro_cirurgico', 'chefe_cardiologia',
    'chefe_clinico_geral', 'chefe_fisioterapeuta', 'chefe_geriatria', 'chefe_ginecologia',
    'chefe_ginecologia_obstetricia', 'chefe_medicina_intensiva', 'chefe_neurologia',
    'chefe_obstetricia', 'chefe_oftalmologia_otorrino', 'chefe_oncologia_clinica',
    'chefe_ortopedista', 'chefe_pediatria', 'chefe_psicologo', 'chefe_psiquiatria',
    'chefe_traumatologista', 'chefe_residencia'
}
MEDICAL_ROLES = {'medico', 'medico_plantonista', 'medico_residente', 'estudante'} | SECTOR_CHIEF_ROLES | {'diretor_clinico', 'diretor_medico'}
NURSING_ROLES = {'enfermeiro', 'enfermeiro_chefe', 'enfermeiro_supervisor', 'diretor_enfermagem'}
FINANCE_ROLES = {'financeiro', 'diretor_administrativo'}
OPERATIONAL_ROLES = {'recepcao', 'laboratorio'}

COMMON_MODULES = {'dashboard', 'portal-paciente'}
MEDICAL_MODULES = {
    'dashboard', 'pacientes', 'agenda', 'atendimentos', 'prontuario', 'leitos', 'internacoes',
    'exames', 'modelos-exames', 'documentos', 'doacao-sangue', 'obstetricia', 'gesso', 'mensagens-rapidas',
    'arquivados', 'relatorios', 'portal-paciente'
}
NURSING_MODULES = {
    'dashboard', 'pacientes', 'agenda', 'atendimentos', 'prontuario', 'leitos', 'internacoes',
    'doacao-sangue', 'gesso', 'arquivados', 'portal-paciente'
}
FINANCE_MODULES = {'dashboard', 'pacientes', 'financeiro', 'produtos', 'convenios', 'planos-saude', 'relatorios', 'arquivados'}
ADMIN_MODULES = {'*'}

ROLE_MODULES = {
    **{role: ADMIN_MODULES for role in ADMIN_ROLES},
    **{role: MEDICAL_MODULES | {'administracao', 'cargos', 'produtos', 'convenios', 'financeiro'} for role in DIRECTION_ROLES},
    **{role: MEDICAL_MODULES | {'cargos'} for role in SECTOR_CHIEF_ROLES},
    'medico': MEDICAL_MODULES,
    'medico_plantonista': MEDICAL_MODULES - {'relatorios'},
    'medico_residente': {'dashboard', 'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos', 'mensagens-rapidas'},
    'estudante': {'dashboard', 'pacientes', 'agenda', 'atendimentos', 'prontuario'},
    'enfermeiro_chefe': NURSING_MODULES | {'relatorios'},
    'enfermeiro_supervisor': NURSING_MODULES,
    'enfermeiro': NURSING_MODULES,
    'recepcao': {'dashboard', 'pacientes', 'agenda', 'arquivados'},
    'financeiro': FINANCE_MODULES,
    'laboratorio': {'dashboard', 'pacientes', 'exames', 'modelos-exames', 'documentos', 'arquivados'},
    'paciente': {'portal-paciente'},
}

SPECIALTY_MODULES = {
    'cardiologia': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos', 'relatorios'},
    'clinico-geral': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos', 'internacoes'},
    'fisioterapeuta': {'pacientes', 'agenda', 'prontuario', 'documentos'},
    'geriatria': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'internacoes', 'exames', 'modelos-exames', 'documentos'},
    'ginecologia': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos'},
    'ginecologia-e-obstetricia': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos', 'obstetricia'},
    'medicina-intensiva': {'pacientes', 'atendimentos', 'prontuario', 'leitos', 'internacoes', 'exames', 'modelos-exames', 'documentos'},
    'neurologia': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos'},
    'obstetricia': {'pacientes', 'agenda', 'prontuario', 'obstetricia', 'documentos'},
    'oftalmologia-e-otorrino': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos'},
    'oncologia-clinica': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos', 'internacoes'},
    'ortopedista': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos', 'gesso'},
    'pediatria': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos'},
    'psicologo': {'pacientes', 'agenda', 'prontuario', 'documentos'},
    'psiquiatria': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'documentos'},
    'traumatologista': {'pacientes', 'agenda', 'atendimentos', 'prontuario', 'exames', 'modelos-exames', 'documentos', 'gesso', 'leitos'},
    'estudante': {'pacientes', 'agenda', 'atendimentos', 'prontuario'},
}

MODULE_PERMISSIONS = {
    'dashboard': 'dashboard.view', 'pacientes': 'patients.view', 'agenda': 'appointments.view',
    'atendimentos': 'medical_records.create', 'prontuario': 'medical_records.view',
    'leitos': 'beds.view', 'internacoes': 'admissions.view', 'exames': 'exams.view', 'modelos-exames': 'exam_templates.view',
    'documentos': 'documents.view', 'doacao-sangue': 'blood_donation.view',
    'obstetricia': 'obstetrics.view', 'gesso': 'plaster.view', 'planos-saude': 'insurance.view',
    'produtos': 'products.view', 'convenios': 'insurance_providers.view', 'financeiro': 'finance.view',
    'mensagens-rapidas': 'quick_messages.view', 'arquivados': 'archive.view',
    'relatorios': 'reports.view', 'administracao': 'admin_panel.view', 'cargos': 'roles.view',
    'portal-paciente': 'patient_portal.view',
}


def get_profile(user):
    return getattr(user, 'profile', None)


def get_role(user):
    profile = get_profile(user)
    return getattr(profile, 'role', '') if profile else ''


def is_patient(user):
    return get_role(user) == 'paciente'


def is_medical(user):
    return get_role(user) in MEDICAL_ROLES


def can_access_module(user, module_slug):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = get_profile(user)
    if not profile or not profile.is_active_profile:
        return False
    if profile.can_manage_system:
        return True
    role_modules = ROLE_MODULES.get(profile.role, set())
    if '*' in role_modules or module_slug in role_modules:
        return True
    try:
        specialty_slugs = [us.specialty.slug for us in user.user_specialties.select_related('specialty').all()]
    except Exception:
        specialty_slugs = []
    for slug in specialty_slugs:
        if module_slug in SPECIALTY_MODULES.get(slug, set()):
            return True
    return False


def can_manage_admin(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = get_profile(user)
    return bool(profile and (profile.role in ADMIN_ROLES or profile.can_manage_system))


def can_manage_roles(user):
    if can_manage_admin(user):
        return True
    return get_role(user) in {'diretor', 'vice_diretor'}


def can_manage_finance(user):
    return can_manage_admin(user) or get_role(user) in FINANCE_ROLES or get_role(user) in DIRECTION_ROLES


def module_required(module_slug):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if can_access_module(request.user, module_slug):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Você não tem permissão para acessar este módulo.')
            if request.user.is_authenticated and is_patient(request.user):
                return redirect('patient_portal')
            return redirect('dashboard')
        return wrapper
    return decorator
