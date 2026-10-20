from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from hospital.models import (
    Bed,
    InsuranceProvider,
    HealthInsurancePlan,
    Patient,
    Product,
    Role,
    Specialty,
    SystemSetting,
    UserProfile,
    UserSpecialty,
)


SPECIALTIES = [
    'Cardiologia', 'Clínico Geral', 'Fisioterapeuta', 'Geriatria', 'Ginecologia',
    'Ginecologia e Obstetrícia', 'Medicina Intensiva', 'Neurologia', 'Obstetrícia',
    'Oftalmologia e Otorrino', 'Oncologia Clínica', 'Ortopedista', 'Pediatria',
    'Psicólogo', 'Psiquiatria', 'Traumatologista', 'Estudante',
]

ROLE_SEED = [
    ('super_admin', 'Superadministrador'), ('admin', 'Administrador Hospitalar'), ('presidente_hospital', 'Presidente do Hospital'),
    ('diretor', 'Diretor'), ('vice_diretor', 'Vice Diretor'), ('diretor_clinico', 'Diretor Clínico'),
    ('diretor_medico', 'Diretor Médico'), ('diretor_administrativo', 'Diretor Administrativo'), ('diretor_enfermagem', 'Diretor de Enfermagem'),
    ('chefe_emergencia', 'Chefe da Emergência'), ('chefe_uti', 'Chefe da UTI'), ('chefe_centro_cirurgico', 'Chefe do Centro Cirúrgico'),
    ('chefe_cardiologia', 'Chefe Cardiologia'), ('chefe_clinico_geral', 'Chefe Clínico Geral'), ('chefe_fisioterapeuta', 'Chefe Fisioterapeuta'),
    ('chefe_geriatria', 'Chefe Geriatria'), ('chefe_ginecologia', 'Chefe Ginecologia'), ('chefe_ginecologia_obstetricia', 'Chefe Ginecologia e Obstetrícia'),
    ('chefe_medicina_intensiva', 'Chefe Medicina Intensiva'), ('chefe_neurologia', 'Chefe Neurologia'), ('chefe_obstetricia', 'Chefe Obstetrícia'),
    ('chefe_oftalmologia_otorrino', 'Chefe Oftalmologia e Otorrino'), ('chefe_oncologia_clinica', 'Chefe Oncologia Clínica'), ('chefe_ortopedista', 'Chefe Ortopedista'),
    ('chefe_pediatria', 'Chefe Pediatria'), ('chefe_psicologo', 'Chefe Psicólogo'), ('chefe_psiquiatria', 'Chefe Psiquiatria'), ('chefe_traumatologista', 'Chefe Traumatologista'),
    ('medico', 'Médico Especialista'), ('medico_plantonista', 'Médico Plantonista'), ('chefe_residencia', 'Chefe de Residência'), ('medico_residente', 'Médico Residente'),
    ('enfermeiro_chefe', 'Enfermeiro Chefe'), ('enfermeiro_supervisor', 'Enfermeiro Supervisor'), ('enfermeiro', 'Enfermeiro'),
    ('recepcao', 'Recepção'), ('financeiro', 'Financeiro'), ('laboratorio', 'Laboratório / Exames'), ('paciente', 'Paciente'), ('estudante', 'Estudante'),
]

SETTINGS = {
    'hospital_name': 'Centro Médico SHINE',
    'theme': 'dark-green',
    'currency': 'BRL',
    'receipt_footer': 'Obrigado pela confiança no Centro Médico SHINE.',
    'document_footer': 'Documento gerado pelo sistema Centro Médico SHINE.',
    'discord_oauth_mode': 'prepared_disabled',
}


def create_user(username, email, password, role, display_name, patient=None, is_staff=False, is_superuser=False):
    user, created = User.objects.get_or_create(username=username, defaults={
        'email': email,
        'first_name': display_name.split(' ')[0],
        'last_name': ' '.join(display_name.split(' ')[1:]),
        'is_staff': is_staff,
        'is_superuser': is_superuser,
    })
    if created:
        user.set_password(password)
        user.save()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.display_name = display_name
    profile.linked_patient = patient
    profile.can_manage_system = role in {'super_admin', 'admin', 'presidente_hospital'} or is_superuser
    profile.can_view_sensitive_records = role != 'paciente'
    profile.save()
    return user


class Command(BaseCommand):
    help = 'Cria dados base, cargos, especialidades, produtos, convênios e contas de teste.'

    def handle(self, *args, **options):
        for slug, name in ROLE_SEED:
            Role.objects.update_or_create(slug=slug, defaults={'name': name, 'is_active': True})

        specialty_objects = {}
        for name in SPECIALTIES:
            specialty, _ = Specialty.objects.get_or_create(name=name)
            specialty_objects[name] = specialty

        for number in range(1, 11):
            Bed.objects.get_or_create(name=f'Leito {number:02d}', defaults={'status': 'Vago'})

        for key, value in SETTINGS.items():
            SystemSetting.objects.update_or_create(key=key, defaults={'value': value, 'is_public': True})

        convenio, _ = InsuranceProvider.objects.get_or_create(
            name='Empresa Alien',
            defaults={'default_discount_percent': Decimal('30.00'), 'contact': 'rh@alien.local', 'is_active': True},
        )
        InsuranceProvider.objects.get_or_create(
            name='Empresa Particular / Sem Convênio',
            defaults={'default_discount_percent': Decimal('0.00'), 'is_active': True},
        )

        product_seed = [
            ('Consulta Ortopedista', 'Consulta especializada com avaliação clínica.', Decimal('1000.00'), 'Consulta', 0),
            ('Consulta Clínica Geral', 'Atendimento clínico geral.', Decimal('450.00'), 'Consulta', 0),
            ('Kit Curativo', 'Material para curativo e procedimentos.', Decimal('120.00'), 'Material', 50),
            ('Retirada de Gesso', 'Procedimento de retirada e orientação.', Decimal('250.00'), 'Procedimento', 0),
        ]
        for name, desc, price, category, stock in product_seed:
            Product.objects.update_or_create(name=name, defaults={
                'description': desc, 'price': price, 'category': category, 'stock': stock,
                'discount_allowed': True, 'applicable_provider': convenio, 'is_active': True,
            })

        patient, _ = Patient.objects.get_or_create(
            full_name='Paciente Teste SHINE',
            defaults={'document': 'PAC-001', 'email': 'paciente@shine.local', 'phone': '(11) 90000-0000', 'company_provider': convenio, 'status': 'Ativo'},
        )
        if not patient.company_provider_id:
            patient.company_provider = convenio
            patient.save(update_fields=['company_provider', 'updated_at'])

        HealthInsurancePlan.objects.update_or_create(
            titular_patient=patient,
            plan_type='Individual',
            defaults={'discount_percent': Decimal('15.00'), 'value': Decimal('120.00'), 'status': 'Ativo'},
        )

        admin = create_user('admin', 'admin@shine.local', 'admin123456', 'admin', 'Admin SHINE', is_staff=True, is_superuser=True)
        doctor = create_user('medico', 'medico@shine.local', 'medico123456', 'medico', 'Dr. João SHINE', is_staff=True)
        cardiologia = specialty_objects.get('Cardiologia')
        if cardiologia:
            UserSpecialty.objects.get_or_create(user=doctor, specialty=cardiologia, defaults={'is_primary': True, 'can_sign_documents': True})

        self.stdout.write(self.style.SUCCESS('Dados base criados/atualizados com sucesso.'))
        self.stdout.write('Contas de teste:')
        self.stdout.write('  Admin:   admin / admin123456')
        self.stdout.write('  Médico:  medico / medico123456')
