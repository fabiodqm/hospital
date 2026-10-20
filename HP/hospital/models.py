from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True




def validate_safe_upload(file_obj):
    max_size = 5 * 1024 * 1024
    if file_obj.size and file_obj.size > max_size:
        raise ValidationError('O arquivo precisa ter no máximo 5 MB.')
    allowed_ext = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}
    suffix = Path(file_obj.name).suffix.lower()
    if suffix not in allowed_ext:
        raise ValidationError('Formato não permitido. Use JPG, PNG, WEBP ou PDF.')


def validate_safe_image(file_obj):
    max_size = 3 * 1024 * 1024
    if file_obj.size and file_obj.size > max_size:
        raise ValidationError('A imagem precisa ter no máximo 3 MB.')
    allowed_ext = {'.jpg', '.jpeg', '.png', '.webp'}
    suffix = Path(file_obj.name).suffix.lower()
    if suffix not in allowed_ext:
        raise ValidationError('Formato de imagem não permitido. Use JPG, PNG ou WEBP.')

class Specialty(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Role(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


BLOOD_TYPE_CHOICES = [('+A', '+A'), ('-A', '-A'), ('+B', '+B'), ('-B', '-B')]


class Patient(TimeStampedModel):
    GENDER_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
        ('Outro', 'Outro'),
        ('Não informado', 'Não informado'),
    ]
    STATUS_CHOICES = [
        ('Ativo', 'Ativo'),
        ('Arquivado', 'Arquivado'),
        ('Bloqueado', 'Bloqueado'),
    ]
    BLOOD_CHOICES = BLOOD_TYPE_CHOICES
    RH_CHOICES = [('+', '+'), ('-', '-'), ('Não informado', 'Não informado')]

    full_name = models.CharField(max_length=180)
    document = models.CharField(max_length=80, blank=True, verbose_name='Passaporte ou documento')
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, blank=True)
    address = models.CharField(max_length=255, blank=True)
    emergency_contact = models.CharField(max_length=180, blank=True)
    blood_type = models.CharField(max_length=30, choices=BLOOD_CHOICES, blank=True)
    rh_factor = models.CharField(max_length=30, choices=RH_CHOICES, blank=True)
    notes = models.TextField(blank=True)
    company_provider = models.ForeignKey('InsuranceProvider', null=True, blank=True, on_delete=models.SET_NULL, related_name='company_patients', verbose_name='Empresa / convênio empresarial')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Ativo')

    class Meta:
        ordering = ['full_name']
        indexes = [models.Index(fields=['full_name']), models.Index(fields=['document'])]

    def __str__(self):
        return self.full_name


class UserProfile(TimeStampedModel):
    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_ADMIN = 'admin'
    ROLE_PRESIDENT = 'presidente_hospital'
    ROLE_DIRECTOR = 'diretor'
    ROLE_VICE_DIRECTOR = 'vice_diretor'
    ROLE_CLINICAL_DIRECTOR = 'diretor_clinico'
    ROLE_MEDICAL_DIRECTOR = 'diretor_medico'
    ROLE_ADMIN_DIRECTOR = 'diretor_administrativo'
    ROLE_NURSING_DIRECTOR = 'diretor_enfermagem'
    ROLE_DOCTOR = 'medico'
    ROLE_ON_CALL_DOCTOR = 'medico_plantonista'
    ROLE_RESIDENCY_CHIEF = 'chefe_residencia'
    ROLE_RESIDENT = 'medico_residente'
    ROLE_NURSE_CHIEF = 'enfermeiro_chefe'
    ROLE_NURSE_SUPERVISOR = 'enfermeiro_supervisor'
    ROLE_NURSE = 'enfermeiro'
    ROLE_RECEPTION = 'recepcao'
    ROLE_FINANCE = 'financeiro'
    ROLE_LAB = 'laboratorio'
    ROLE_PATIENT = 'paciente'
    ROLE_STUDENT = 'estudante'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Superadministrador'),
        (ROLE_ADMIN, 'Administrador Hospitalar'),
        (ROLE_PRESIDENT, 'Presidente do Hospital'),
        (ROLE_DIRECTOR, 'Diretor'),
        (ROLE_VICE_DIRECTOR, 'Vice Diretor'),
        (ROLE_CLINICAL_DIRECTOR, 'Diretor Clínico'),
        (ROLE_MEDICAL_DIRECTOR, 'Diretor Médico'),
        (ROLE_ADMIN_DIRECTOR, 'Diretor Administrativo'),
        (ROLE_NURSING_DIRECTOR, 'Diretor de Enfermagem'),
        (ROLE_DOCTOR, 'Médico Especialista'),
        (ROLE_ON_CALL_DOCTOR, 'Médico Plantonista'),
        (ROLE_RESIDENCY_CHIEF, 'Chefe de Residência'),
        (ROLE_RESIDENT, 'Médico Residente'),
        (ROLE_NURSE_CHIEF, 'Enfermeiro Chefe'),
        (ROLE_NURSE_SUPERVISOR, 'Enfermeiro Supervisor'),
        (ROLE_NURSE, 'Enfermeiro'),
        (ROLE_RECEPTION, 'Recepção'),
        (ROLE_FINANCE, 'Financeiro'),
        (ROLE_LAB, 'Laboratório / Exames'),
        (ROLE_PATIENT, 'Paciente'),
        (ROLE_STUDENT, 'Estudante'),
        ('chefe_emergencia', 'Chefe da Emergência'),
        ('chefe_uti', 'Chefe da UTI'),
        ('chefe_centro_cirurgico', 'Chefe do Centro Cirúrgico'),
        ('chefe_cardiologia', 'Chefe Cardiologia'),
        ('chefe_clinico_geral', 'Chefe Clínico Geral'),
        ('chefe_fisioterapeuta', 'Chefe Fisioterapeuta'),
        ('chefe_geriatria', 'Chefe Geriatria'),
        ('chefe_ginecologia', 'Chefe Ginecologia'),
        ('chefe_ginecologia_obstetricia', 'Chefe Ginecologia e Obstetrícia'),
        ('chefe_medicina_intensiva', 'Chefe Medicina Intensiva'),
        ('chefe_neurologia', 'Chefe Neurologia'),
        ('chefe_obstetricia', 'Chefe Obstetrícia'),
        ('chefe_oftalmologia_otorrino', 'Chefe Oftalmologia e Otorrino'),
        ('chefe_oncologia_clinica', 'Chefe Oncologia Clínica'),
        ('chefe_ortopedista', 'Chefe Ortopedista'),
        ('chefe_pediatria', 'Chefe Pediatria'),
        ('chefe_psicologo', 'Chefe Psicólogo'),
        ('chefe_psiquiatria', 'Chefe Psiquiatria'),
        ('chefe_traumatologista', 'Chefe Traumatologista'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    display_name = models.CharField(max_length=140, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    signature_image = models.ImageField(upload_to='signatures/', blank=True, null=True, validators=[validate_safe_image])
    signature_registered_at = models.DateTimeField(null=True, blank=True)
    professional_license = models.CharField(max_length=80, blank=True, help_text='CRM, COREN, CRP ou registro profissional.')
    linked_patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.SET_NULL, related_name='portal_users')
    discord_id = models.CharField(max_length=80, blank=True, db_index=True)
    discord_username = models.CharField(max_length=120, blank=True)
    discord_verified = models.BooleanField(default=False)
    can_manage_system = models.BooleanField(default=False)
    can_view_sensitive_records = models.BooleanField(default=False)
    is_active_profile = models.BooleanField(default=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return self.display_name or self.user.get_full_name() or self.user.username

    @property
    def is_admin_level(self):
        return self.role in {self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_PRESIDENT} or self.user.is_superuser


class UserSpecialty(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_specialties')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    can_attend = models.BooleanField(default=True)
    can_sign_documents = models.BooleanField(default=False)
    can_access_records = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'specialty')
        ordering = ['user__username', 'specialty__name']

    def __str__(self):
        return f'{self.user.username} - {self.specialty.name}'


class StudentSupervision(TimeStampedModel):
    student_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_supervisions')
    supervisor_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervised_students')
    specialty = models.ForeignKey(Specialty, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['student_user__username']

    def __str__(self):
        return f'{self.student_user.username} supervisionado por {self.supervisor_user.username}'


class Appointment(TimeStampedModel):
    STATUS_CHOICES = [
        ('Agendada', 'Agendada'),
        ('Confirmada', 'Confirmada'),
        ('Em atendimento', 'Em atendimento'),
        ('Finalizada', 'Finalizada'),
        ('Cancelada', 'Cancelada'),
        ('Faltou', 'Faltou'),
        ('Arquivada', 'Arquivada'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='appointments_as_doctor')
    specialty = models.ForeignKey(Specialty, null=True, blank=True, on_delete=models.SET_NULL)
    scheduled_at = models.DateTimeField()
    anamnesis = models.TextField(blank=True)
    exams_requested = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Agendada')

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'{self.patient} - {self.scheduled_at:%d/%m/%Y %H:%M}'


class MedicalRecord(TimeStampedModel):
    STATUS_CHOICES = [
        ('Rascunho', 'Rascunho'),
        ('Aguardando aprovação', 'Aguardando aprovação'),
        ('Finalizado', 'Finalizado'),
        ('Arquivado', 'Arquivado'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='medical_records')
    student_author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='student_medical_records')
    supervisor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='supervised_medical_records')
    specialty = models.ForeignKey(Specialty, null=True, blank=True, on_delete=models.SET_NULL)
    appointment = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.SET_NULL)
    attendance_date = models.DateField(default=timezone.localdate)
    general_condition = models.CharField(max_length=120, blank=True)
    blood_pressure = models.CharField(max_length=40, blank=True)
    heart_rate = models.CharField(max_length=40, blank=True)
    respiratory_rate = models.CharField(max_length=40, blank=True)
    temperature = models.CharField(max_length=40, blank=True)
    spo2 = models.CharField(max_length=40, blank=True)
    anamnesis = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    conduct = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    orientations = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Rascunho')

    class Meta:
        ordering = ['-attendance_date', '-created_at']

    def __str__(self):
        return f'Atendimento de {self.patient} em {self.attendance_date:%d/%m/%Y}'


class Bed(TimeStampedModel):
    STATUS_CHOICES = [
        ('Vago', 'Vago'),
        ('Ocupado', 'Ocupado'),
        ('Reservado', 'Reservado'),
        ('Manutenção', 'Manutenção'),
        ('Arquivado', 'Arquivado'),
    ]
    name = models.CharField(max_length=80, unique=True)
    ward = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Vago')
    current_patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.SET_NULL, related_name='current_beds')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Admission(TimeStampedModel):
    STATUS_CHOICES = [
        ('Ativa', 'Ativa'),
        ('Alta', 'Alta'),
        ('Transferida', 'Transferida'),
        ('Cancelada', 'Cancelada'),
        ('Arquivada', 'Arquivada'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='admissions_as_doctor')
    bed = models.ForeignKey(Bed, null=True, blank=True, on_delete=models.SET_NULL, related_name='admissions')
    specialty = models.ForeignKey(Specialty, null=True, blank=True, on_delete=models.SET_NULL)
    entry_date = models.DateField(default=timezone.localdate)
    expected_discharge = models.DateField(null=True, blank=True)
    discharge_date = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    general_condition = models.CharField(max_length=120, blank=True)
    blood_pressure = models.CharField(max_length=40, blank=True)
    heart_rate = models.CharField(max_length=40, blank=True)
    respiratory_rate = models.CharField(max_length=40, blank=True)
    temperature = models.CharField(max_length=40, blank=True)
    spo2 = models.CharField(max_length=40, blank=True)
    initial_diagnosis = models.TextField(blank=True)
    conduct = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    orientations = models.TextField(blank=True)
    discharge_reason = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Ativa')

    class Meta:
        ordering = ['-entry_date']

    def __str__(self):
        return f'Internação - {self.patient}'


class ExamTemplate(TimeStampedModel):
    CATEGORY_CHOICES = [
        ('Laboratorial', 'Laboratorial'),
        ('Imagem', 'Imagem'),
        ('Cardiologia', 'Cardiologia'),
        ('Neurologia', 'Neurologia'),
        ('Pneumologia', 'Pneumologia'),
        ('Ginecologia/Obstetrícia', 'Ginecologia/Obstetrícia'),
        ('Endoscopia', 'Endoscopia'),
        ('Patologia', 'Patologia'),
        ('Oftalmologia/Otorrino', 'Oftalmologia/Otorrino'),
        ('Outros', 'Outros'),
    ]
    name = models.CharField(max_length=180, unique=True)
    category = models.CharField(max_length=60, choices=CATEGORY_CHOICES, default='Laboratorial')
    exam_type = models.CharField(max_length=180)
    body_system = models.CharField(max_length=120, blank=True)
    sample_material = models.CharField(max_length=140, blank=True)
    clinical_indication = models.TextField(blank=True)
    preparation = models.TextField(blank=True)
    template_content = models.TextField(help_text='Modelo editável do laudo/solicitação médica.')
    conclusion_template = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Modelo de exame'
        verbose_name_plural = 'Modelos de exames'
        indexes = [models.Index(fields=['category', 'is_active']), models.Index(fields=['exam_type'])]

    def __str__(self):
        return self.name


class Exam(TimeStampedModel):
    STATUS_CHOICES = [
        ('Solicitado', 'Solicitado'),
        ('Em análise', 'Em análise'),
        ('Finalizado', 'Finalizado'),
        ('Entregue ao paciente', 'Entregue ao paciente'),
        ('Arquivado', 'Arquivado'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='exams')
    requesting_doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='requested_exams')
    template = models.ForeignKey(ExamTemplate, null=True, blank=True, on_delete=models.SET_NULL, related_name='exams')
    exam_type = models.CharField(max_length=160)
    clinical_indication = models.TextField(blank=True)
    sample_material = models.CharField(max_length=140, blank=True)
    issue_date = models.DateField(default=timezone.localdate)
    report = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    attachment = models.FileField(upload_to='exams/', null=True, blank=True, validators=[validate_safe_upload])
    signed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='signed_exams')
    signed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Solicitado')

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f'{self.exam_type} - {self.patient}'


class MedicalDocument(TimeStampedModel):
    STATUS_CHOICES = [
        ('Rascunho', 'Rascunho'),
        ('Emitido', 'Emitido'),
        ('Entregue', 'Entregue'),
        ('Arquivado', 'Arquivado'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    requesting_doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='medical_documents')
    document_type = models.CharField(max_length=160)
    issue_date = models.DateField(default=timezone.localdate)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Rascunho')

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f'{self.document_type} - {self.patient}'


class BloodDonationScreening(TimeStampedModel):
    RESULT_CHOICES = [
        ('Apto', 'Apto'),
        ('Inapto temporário', 'Inapto temporário'),
        ('Inapto definitivo', 'Inapto definitivo'),
        ('Pendente de avaliação', 'Pendente de avaliação'),
        ('Arquivado', 'Arquivado'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='blood_donations')
    doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    collection_date = models.DateField(default=timezone.localdate)
    blood_type = models.CharField(max_length=30, choices=BLOOD_TYPE_CHOICES, blank=True)
    rh_factor = models.CharField(max_length=30, blank=True)
    feels_healthy = models.BooleanField(default=False)
    recent_tattoo_or_piercing = models.BooleanField(default=False)
    uses_medication = models.BooleanField(default=False)
    had_fever = models.BooleanField(default=False)
    had_surgery = models.BooleanField(default=False)
    is_fasting = models.BooleanField(default=False)
    donated_before = models.BooleanField(default=False)
    observations = models.TextField(blank=True)
    result = models.CharField(max_length=50, choices=RESULT_CHOICES, default='Pendente de avaliação')

    class Meta:
        ordering = ['-collection_date']

    def __str__(self):
        return f'Doação de sangue - {self.patient}'


class PregnancyFollowUp(TimeStampedModel):
    STATUS_CHOICES = [('Ativo', 'Ativo'), ('Finalizado', 'Finalizado'), ('Arquivado', 'Arquivado')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pregnancies')
    doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    start_date = models.DateField()
    real_days = models.PositiveIntegerField(default=280)
    consultation_count = models.PositiveIntegerField(default=8)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Ativo')

    class Meta:
        ordering = ['-start_date']

    @property
    def probable_birth_date(self):
        return self.start_date + timezone.timedelta(days=280)

    def __str__(self):
        return f'Gestação - {self.patient}'


class PlasterRecord(TimeStampedModel):
    STATUS_CHOICES = [('Ativo', 'Ativo'), ('Retirado', 'Retirado'), ('Atrasado', 'Atrasado'), ('Cancelado', 'Cancelado'), ('Arquivado', 'Arquivado')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='plaster_records')
    doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    body_part = models.CharField(max_length=120)
    immobilization_type = models.CharField(max_length=120, blank=True)
    placement_date = models.DateField(default=timezone.localdate)
    removal_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Ativo')

    class Meta:
        ordering = ['-placement_date']

    def __str__(self):
        return f'Gesso - {self.patient}'


class InsuranceProvider(TimeStampedModel):
    name = models.CharField(max_length=140, unique=True)
    default_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contact = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Convênio'
        verbose_name_plural = 'Convênios'

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    CATEGORY_CHOICES = [
        ('Consulta', 'Consulta'),
        ('Procedimento', 'Procedimento'),
        ('Medicamento', 'Medicamento'),
        ('Material', 'Material'),
        ('Serviço', 'Serviço'),
        ('Outros', 'Outros'),
    ]
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True, validators=[validate_safe_image])
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='Serviço')
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    discount_allowed = models.BooleanField(default=True)
    applicable_provider = models.ForeignKey(InsuranceProvider, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')

    class Meta:
        ordering = ['category', 'name']
        indexes = [models.Index(fields=['name']), models.Index(fields=['category'])]
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.name


class HealthInsurancePlan(TimeStampedModel):
    STATUS_CHOICES = [('Ativo', 'Ativo'), ('Vencido', 'Vencido'), ('Cancelado', 'Cancelado'), ('Suspenso', 'Suspenso'), ('Arquivado', 'Arquivado')]
    PLAN_CHOICES = [('Individual', 'Individual'), ('Familiar', 'Familiar')]
    plan_type = models.CharField(max_length=80, choices=PLAN_CHOICES, default='Individual')
    provider = models.ForeignKey(InsuranceProvider, null=True, blank=True, on_delete=models.SET_NULL, related_name='plans', verbose_name='Empresa vinculada (opcional)')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Desconto do plano (%)')
    titular_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_plans')
    dependents = models.ManyToManyField(Patient, blank=True, related_name='dependent_insurance_plans')
    responsible_doctor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    sale_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Ativo')

    class Meta:
        ordering = ['-sale_date']

    def __str__(self):
        return f'{self.plan_type} - {self.titular_patient}'


class Sale(TimeStampedModel):
    STATUS_CHOICES = [('Aberta', 'Aberta'), ('Finalizada', 'Finalizada'), ('Cancelada', 'Cancelada'), ('Arquivada', 'Arquivada')]
    patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales')
    operator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales_as_operator')
    provider = models.ForeignKey(InsuranceProvider, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales', verbose_name='Convênio aplicado')
    original_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_applied_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales_discount_applied')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_source = models.CharField(max_length=255, blank=True, verbose_name='Origem do desconto')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    receipt_text = models.TextField(blank=True)
    payment_proof = models.FileField(upload_to='payments/', null=True, blank=True, validators=[validate_safe_upload])
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Aberta')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Venda #{self.pk or "nova"}'


class SaleItem(TimeStampedModel):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, related_name='sale_items')
    product_name = models.CharField(max_length=140)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product_name


class QuickMessage(TimeStampedModel):
    CATEGORY_CHOICES = [('Atendimento', 'Atendimento'), ('Emergência', 'Emergência'), ('Alta médica', 'Alta médica'), ('Avisos', 'Avisos'), ('Prescrição', 'Prescrição'), ('Procedimentos', 'Procedimentos'), ('Convocação', 'Convocação'), ('Financeiro', 'Financeiro'), ('Geral', 'Geral'), ('Arquivado', 'Arquivado')]
    prefix = models.CharField(max_length=120, blank=True)
    message = models.TextField()
    initial_emojis = models.CharField(max_length=80, blank=True)
    final_emojis = models.CharField(max_length=80, blank=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='Geral')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_favorite', '-created_at']

    def __str__(self):
        return self.message[:80]


class RoleChangeLog(TimeStampedModel):
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='role_changes_made')
    changed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_changes_received')
    previous_role = models.CharField(max_length=80, blank=True)
    new_role = models.CharField(max_length=80)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log de alteração de cargo'
        verbose_name_plural = 'Logs de alteração de cargos'

    def __str__(self):
        return f'{self.changed_user} {self.previous_role} -> {self.new_role}'


class SystemSetting(TimeStampedModel):
    key = models.CharField(max_length=120, unique=True)
    value = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['key']

    def __str__(self):
        return self.key


class AuditLog(TimeStampedModel):
    ACTION_CHOICES = [
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('archive', 'Arquivamento'),
        ('login', 'Entrada'),
        ('permission', 'Permissão'),
        ('role_change', 'Alteração de cargo'),
        ('security', 'Segurança'),
        ('error', 'Erro'),
    ]
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=40, choices=ACTION_CHOICES)
    module = models.CharField(max_length=80, blank=True)
    object_label = models.CharField(max_length=180, blank=True)
    object_id = models.CharField(max_length=80, blank=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} - {self.module} - {self.created_at:%d/%m/%Y %H:%M}'


class ArchivedRecord(TimeStampedModel):
    module = models.CharField(max_length=80)
    object_label = models.CharField(max_length=180)
    object_id = models.CharField(max_length=80)
    archived_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.module}: {self.object_label}'


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
