from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    Admission,
    Appointment,
    Bed,
    BLOOD_TYPE_CHOICES,
    BloodDonationScreening,
    Exam,
    ExamTemplate,
    HealthInsurancePlan,
    InsuranceProvider,
    MedicalDocument,
    MedicalRecord,
    Patient,
    PlasterRecord,
    PregnancyFollowUp,
    Product,
    QuickMessage,
    RoleChangeLog,
    Sale,
    Specialty,
    SystemSetting,
    UserProfile,
    UserSpecialty,
    validate_safe_image,
)

BASE_INPUT = 'w-full rounded-2xl border border-emerald-900/50 bg-slate-950/70 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-500/20'
CHECK_INPUT = 'h-5 w-5 rounded border-emerald-800 bg-slate-950 text-emerald-500 focus:ring-emerald-500/30'

DOCTOR_ROLE_SLUGS = {
    'medico', 'medico_plantonista', 'medico_residente', 'chefe_residencia',
    'diretor_clinico', 'diretor_medico',
    'chefe_emergencia', 'chefe_uti', 'chefe_centro_cirurgico', 'chefe_cardiologia',
    'chefe_clinico_geral', 'chefe_fisioterapeuta', 'chefe_geriatria',
    'chefe_ginecologia', 'chefe_ginecologia_obstetricia',
    'chefe_medicina_intensiva', 'chefe_neurologia', 'chefe_obstetricia',
    'chefe_oftalmologia_otorrino', 'chefe_oncologia_clinica',
    'chefe_ortopedista', 'chefe_pediatria', 'chefe_psicologo',
    'chefe_psiquiatria', 'chefe_traumatologista',
}
DOCTOR_USER_FIELD_NAMES = {
    'doctor', 'requesting_doctor', 'responsible_doctor', 'signed_by', 'supervisor',
}
ROLE_CHOICES_WITHOUT_PATIENT = [
    choice for choice in UserProfile.ROLE_CHOICES if choice[0] != UserProfile.ROLE_PATIENT
]
EMPTY_BLOOD_TYPE_CHOICES = [('', 'Selecione o tipo sanguíneo')] + BLOOD_TYPE_CHOICES
PLASTER_BODY_PART_CHOICES = [
    ('', 'Selecione a parte do corpo'),
    ('Clavícula', 'Clavícula'),
    ('Ombro', 'Ombro'),
    ('Braço / úmero', 'Braço / úmero'),
    ('Cotovelo', 'Cotovelo'),
    ('Antebraço / rádio e ulna', 'Antebraço / rádio e ulna'),
    ('Punho', 'Punho'),
    ('Mão', 'Mão'),
    ('Metacarpos', 'Metacarpos'),
    ('Polegar', 'Polegar'),
    ('Dedos da mão', 'Dedos da mão'),
    ('Coluna cervical', 'Coluna cervical'),
    ('Coluna torácica', 'Coluna torácica'),
    ('Coluna lombar', 'Coluna lombar'),
    ('Quadril / pelve', 'Quadril / pelve'),
    ('Coxa / fêmur', 'Coxa / fêmur'),
    ('Joelho', 'Joelho'),
    ('Patela', 'Patela'),
    ('Perna / tíbia e fíbula', 'Perna / tíbia e fíbula'),
    ('Tornozelo', 'Tornozelo'),
    ('Calcâneo', 'Calcâneo'),
    ('Pé', 'Pé'),
    ('Metatarsos', 'Metatarsos'),
    ('Dedos do pé', 'Dedos do pé'),
    ('Outro', 'Outro / escrever manualmente'),
]


def doctor_queryset():
    return User.objects.filter(
        is_active=True,
        profile__is_active_profile=True,
        profile__role__in=DOCTOR_ROLE_SLUGS,
    ).order_by('first_name', 'last_name', 'username').distinct()


def date_input():
    return forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})


def datetime_input():
    return forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'})

FIELD_LABELS = {
    'username': 'Usuário',
    'email': 'E-mail',
    'first_name': 'Nome',
    'last_name': 'Sobrenome',
    'password1': 'Senha',
    'password2': 'Confirmar senha',
    'is_active': 'Usuário ativo',
    'role': 'Perfil de acesso',
    'display_name': 'Nome de exibição',
    'phone': 'Telefone',
    'profile_photo': 'Foto do usuário',
    'specialties': 'Especialidades',
    'can_manage_system': 'Pode administrar o sistema',
    'can_view_sensitive_records': 'Pode ver prontuários sensíveis',
    'is_active_profile': 'Perfil ativo',
    'signature_image': 'Assinatura médica digitalizada',
    'professional_license': 'Registro profissional',
    'signature_registered_at': 'Assinatura cadastrada em',
    'template': 'Modelo de exame',
    'clinical_indication': 'Indicação clínica',
    'sample_material': 'Material / amostra',
    'findings': 'Achados / resultados',
    'conclusion': 'Conclusão diagnóstica',
    'recommendations': 'Recomendações',
    'signed_by': 'Assinado por',
    'signed_at': 'Data da assinatura',
    'body_system': 'Sistema corporal',
    'preparation': 'Preparo do paciente',
    'template_content': 'Modelo editável do laudo',
    'conclusion_template': 'Conclusão padrão',
    'full_name': 'Nome completo',
    'document': 'Passaporte / documento',
    'birth_date': 'Data de nascimento',
    'gender': 'Gênero',
    'address': 'Endereço',
    'emergency_contact': 'Contato de emergência',
    'blood_type': 'Tipo sanguíneo',
    'rh_factor': 'Fator RH',
    'notes': 'Observações',
    'status': 'Situação',
    'company_provider': 'Empresa / convênio empresarial',
    'patient': 'Paciente',
    'doctor': 'Médico responsável',
    'requesting_doctor': 'Médico solicitante',
    'responsible_doctor': 'Médico responsável',
    'specialty': 'Especialidade',
    'scheduled_at': 'Data e hora',
    'anamnesis': 'Anamnese',
    'exams_requested': 'Exames solicitados',
    'student_author': 'Estudante responsável pelo rascunho',
    'supervisor': 'Supervisor',
    'appointment': 'Consulta vinculada',
    'attendance_date': 'Data do atendimento',
    'general_condition': 'Estado geral',
    'blood_pressure': 'Pressão arterial',
    'heart_rate': 'Frequência cardíaca',
    'respiratory_rate': 'Frequência respiratória',
    'temperature': 'Temperatura',
    'spo2': 'SpO₂',
    'diagnosis': 'Diagnóstico',
    'conduct': 'Conduta',
    'treatment': 'Tratamento',
    'orientations': 'Orientações',
    'name': 'Nome',
    'ward': 'Ala / setor',
    'current_patient': 'Paciente atual',
    'bed': 'Leito',
    'entry_date': 'Data de entrada',
    'expected_discharge': 'Previsão de alta',
    'discharge_date': 'Data de alta',
    'reason': 'Motivo',
    'initial_diagnosis': 'Diagnóstico inicial',
    'discharge_reason': 'Motivo da alta',
    'exam_type': 'Tipo de exame',
    'issue_date': 'Data de emissão',
    'report': 'Laudo',
    'attachment': 'Anexo',
    'document_type': 'Tipo de documento',
    'content': 'Conteúdo',
    'collection_date': 'Data da coleta',
    'feels_healthy': 'Está se sentindo saudável?',
    'recent_tattoo_or_piercing': 'Fez tatuagem ou piercing recentemente?',
    'uses_medication': 'Usa medicamentos regularmente?',
    'had_fever': 'Teve febre recentemente?',
    'had_surgery': 'Fez cirurgia recentemente?',
    'is_fasting': 'Está em jejum?',
    'donated_before': 'Já doou sangue antes?',
    'observations': 'Observações',
    'result': 'Resultado',
    'start_date': 'Data de início',
    'real_days': 'Total de dias reais',
    'consultation_count': 'Número de consultas',
    'body_part': 'Parte do corpo',
    'immobilization_type': 'Tipo de imobilização',
    'placement_date': 'Data de colocação',
    'removal_date': 'Data de retirada',
    'plan_type': 'Tipo de plano',
    'titular_patient': 'Paciente titular',
    'dependents': 'Dependentes',
    'sale_date': 'Data da venda',
    'due_date': 'Data de vencimento',
    'value': 'Valor',
    'operator': 'Operador',
    'subtotal': 'Subtotal',
    'discount_percent': 'Desconto (%)',
    'total': 'Total',
    'receipt_text': 'Texto do recibo',
    'payment_proof': 'Comprovante de pagamento',
    'prefix': 'Prefixo',
    'message': 'Mensagem',
    'initial_emojis': 'Emojis iniciais',
    'final_emojis': 'Emojis finais',
    'category': 'Categoria',
    'created_by': 'Criado por',
    'is_favorite': 'Favorito',
    'slug': 'Slug',
    'description': 'Descrição',
    'is_active': 'Ativo',
    'key': 'Chave',
    'provider': 'Empresa vinculada',
    'default_discount_percent': 'Desconto da empresa (%)',
    'contact': 'Contato',
    'product': 'Produto',
    'product_name': 'Nome do produto',
    'image': 'Imagem',
    'price': 'Preço',
    'category': 'Categoria',
    'stock': 'Estoque',
    'discount_allowed': 'Permite desconto',
    'is_active': 'Ativo',
    'original_total': 'Valor original',
    'discount_amount': 'Valor do desconto',
    'discount_source': 'Origem do desconto',
    'discount_applied_by': 'Desconto aplicado por',
    'changed_by': 'Alterado por',
    'changed_user': 'Usuário alterado',
    'previous_role': 'Cargo anterior',
    'new_role': 'Novo cargo',
    'reason': 'Motivo',
    'is_public': 'Público',
}


class StyledModelForm(forms.ModelForm):
    textarea_rows = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = FIELD_LABELS.get(field_name, field.label)
            if field_name in DOCTOR_USER_FIELD_NAMES and hasattr(field, 'queryset'):
                field.queryset = doctor_queryset()
                field.empty_label = 'Selecione um médico'
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', CHECK_INPUT)
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('class', BASE_INPUT + ' min-h-[120px]')
                widget.attrs.setdefault('rows', self.textarea_rows)
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs.setdefault('class', BASE_INPUT + ' min-h-[130px]')
            else:
                widget.attrs.setdefault('class', BASE_INPUT)


class PatientForm(StyledModelForm):
    blood_type = forms.ChoiceField(choices=EMPTY_BLOOD_TYPE_CHOICES, required=False)

    class Meta:
        model = Patient
        fields = ['full_name', 'document', 'phone', 'email', 'birth_date', 'gender', 'address', 'emergency_contact', 'blood_type', 'company_provider', 'notes', 'status']
        widgets = {'birth_date': date_input()}


class AppointmentForm(StyledModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'specialty', 'scheduled_at', 'anamnesis', 'exams_requested', 'status']
        widgets = {'scheduled_at': datetime_input()}


class MedicalRecordForm(StyledModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'doctor', 'student_author', 'supervisor', 'specialty', 'appointment', 'attendance_date',
            'general_condition', 'blood_pressure', 'heart_rate', 'respiratory_rate', 'temperature', 'spo2',
            'anamnesis', 'diagnosis', 'conduct', 'treatment', 'orientations', 'status'
        ]
        widgets = {'attendance_date': date_input()}


class BedForm(StyledModelForm):
    class Meta:
        model = Bed
        fields = ['name', 'ward', 'status', 'current_patient', 'notes']


class AdmissionForm(StyledModelForm):
    class Meta:
        model = Admission
        fields = [
            'patient', 'doctor', 'bed', 'specialty', 'entry_date', 'expected_discharge', 'discharge_date', 'reason',
            'general_condition', 'blood_pressure', 'heart_rate', 'respiratory_rate', 'temperature', 'spo2',
            'initial_diagnosis', 'conduct', 'treatment', 'orientations', 'discharge_reason', 'status'
        ]
        widgets = {
            'entry_date': date_input(),
            'expected_discharge': date_input(),
            'discharge_date': date_input(),
        }


class ExamForm(StyledModelForm):
    sign_now = forms.BooleanField(required=False, label='Assinar este exame agora com minha assinatura cadastrada')

    class Meta:
        model = Exam
        fields = [
            'patient', 'requesting_doctor', 'template', 'exam_type', 'issue_date', 'clinical_indication',
            'sample_material', 'report', 'findings', 'conclusion', 'recommendations', 'attachment', 'status'
        ]
        widgets = {'issue_date': date_input()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = ExamTemplate.objects.filter(is_active=True).order_by('category', 'name')
        self.fields['template'].required = False
        self.fields['template'].help_text = 'Escolha um modelo realista. O texto pode ser editado antes de salvar.'
        self.fields['report'].widget.attrs.setdefault('rows', 12)
        self.fields['findings'].widget.attrs.setdefault('rows', 8)
        self.fields['conclusion'].widget.attrs.setdefault('rows', 5)
        self.fields['recommendations'].widget.attrs.setdefault('rows', 4)


class ExamTemplateForm(StyledModelForm):
    class Meta:
        model = ExamTemplate
        fields = ['name', 'category', 'exam_type', 'body_system', 'sample_material', 'clinical_indication', 'preparation', 'template_content', 'conclusion_template', 'recommendations', 'is_active']


class UserSignatureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['professional_license', 'signature_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = FIELD_LABELS.get(field_name, field.label)
            field.widget.attrs.setdefault('class', BASE_INPUT)
        self.fields['signature_image'].help_text = 'Envie uma imagem PNG, JPG ou WEBP com fundo claro/transparente. Tamanho máximo: 3 MB.'


class UserAccountForm(forms.ModelForm):
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['display_name', 'phone', 'profile_photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = FIELD_LABELS.get(field_name, field.label)
            field.widget.attrs.setdefault('class', BASE_INPUT)
        self.fields['profile_photo'].help_text = 'Use JPG, PNG ou WEBP com ate 3 MB.'
        self.fields['profile_photo'].widget.attrs.setdefault('accept', 'image/png,image/jpeg,image/webp')

    def clean_profile_photo(self):
        profile_photo = self.cleaned_data.get('profile_photo')
        if profile_photo and hasattr(profile_photo, 'content_type'):
            validate_safe_image(profile_photo)
        return profile_photo


class MedicalDocumentForm(StyledModelForm):
    class Meta:
        model = MedicalDocument
        fields = ['patient', 'requesting_doctor', 'document_type', 'issue_date', 'content', 'status']
        widgets = {'issue_date': date_input()}


class BloodDonationScreeningForm(StyledModelForm):
    blood_type = forms.ChoiceField(choices=EMPTY_BLOOD_TYPE_CHOICES, required=False)

    class Meta:
        model = BloodDonationScreening
        fields = [
            'patient', 'doctor', 'collection_date', 'blood_type', 'feels_healthy',
            'recent_tattoo_or_piercing', 'uses_medication', 'had_fever', 'had_surgery', 'is_fasting',
            'donated_before', 'observations', 'result'
        ]
        widgets = {'collection_date': date_input()}


class PregnancyFollowUpForm(StyledModelForm):
    class Meta:
        model = PregnancyFollowUp
        fields = ['patient', 'doctor', 'start_date', 'real_days', 'consultation_count', 'notes', 'status']
        widgets = {'start_date': date_input()}


class PlasterRecordForm(StyledModelForm):
    body_part = forms.ChoiceField(choices=PLASTER_BODY_PART_CHOICES, required=False)
    other_body_part = forms.CharField(
        required=False,
        label='Outra parte do corpo',
        help_text='Preencha somente se a parte do corpo não estiver na lista.',
    )

    class Meta:
        model = PlasterRecord
        fields = ['patient', 'doctor', 'body_part', 'other_body_part', 'immobilization_type', 'placement_date', 'removal_date', 'notes', 'status']
        widgets = {'placement_date': date_input(), 'removal_date': date_input()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        known_values = {value for value, _ in PLASTER_BODY_PART_CHOICES}
        current_body_part = getattr(self.instance, 'body_part', '') if self.instance else ''
        if current_body_part and current_body_part not in known_values:
            self.fields['body_part'].initial = 'Outro'
            self.fields['other_body_part'].initial = current_body_part

    def clean(self):
        cleaned = super().clean()
        selected = cleaned.get('body_part')
        other = (cleaned.get('other_body_part') or '').strip()
        if selected == 'Outro' and not other:
            raise ValidationError('Informe a parte do corpo no campo "Outra parte do corpo".')
        if not selected and not other:
            raise ValidationError('Selecione uma parte do corpo ou preencha o campo manual.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected = self.cleaned_data.get('body_part')
        other = (self.cleaned_data.get('other_body_part') or '').strip()
        instance.body_part = other if selected == 'Outro' else selected
        if commit:
            instance.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return instance


class InsuranceProviderForm(StyledModelForm):
    class Meta:
        model = InsuranceProvider
        fields = ['name', 'default_discount_percent', 'contact', 'notes', 'is_active']


class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'price', 'category', 'stock', 'is_active', 'discount_allowed', 'applicable_provider']


class RoleChangeLogForm(StyledModelForm):
    class Meta:
        model = RoleChangeLog
        fields = ['changed_user', 'previous_role', 'new_role', 'reason']


class HealthInsurancePlanForm(StyledModelForm):
    class Meta:
        model = HealthInsurancePlan
        fields = ['plan_type', 'titular_patient', 'dependents', 'discount_percent', 'responsible_doctor', 'sale_date', 'due_date', 'value', 'notes', 'status']
        widgets = {'sale_date': date_input(), 'due_date': date_input()}


class SaleForm(StyledModelForm):
    class Meta:
        model = Sale
        fields = ['patient', 'operator', 'provider', 'original_total', 'subtotal', 'discount_percent', 'discount_amount', 'discount_source', 'discount_applied_by', 'total', 'receipt_text', 'status']


class QuickMessageForm(StyledModelForm):
    class Meta:
        model = QuickMessage
        fields = ['prefix', 'message', 'initial_emojis', 'final_emojis', 'category', 'is_favorite']


class SpecialtyForm(StyledModelForm):
    class Meta:
        model = Specialty
        fields = ['name', 'slug', 'description', 'is_active']


class SystemSettingForm(StyledModelForm):
    class Meta:
        model = SystemSetting
        fields = ['key', 'value', 'is_public', 'description']


class UserCreatePanelForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    role = forms.ChoiceField(choices=ROLE_CHOICES_WITHOUT_PATIENT)
    display_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    profile_photo = forms.ImageField(required=False)
    signature_image = forms.ImageField(required=False)
    professional_license = forms.CharField(required=False)
    specialties = forms.ModelMultipleChoiceField(queryset=Specialty.objects.filter(is_active=True), required=False)
    can_manage_system = forms.BooleanField(required=False)
    can_view_sensitive_records = forms.BooleanField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = FIELD_LABELS.get(field_name, field.label)
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', CHECK_INPUT)
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.setdefault('class', BASE_INPUT + ' min-h-[130px]')
            else:
                field.widget.attrs.setdefault('class', BASE_INPUT)

    def save(self, commit=True):
        user = super().save(commit=commit)
        user.email = self.cleaned_data.get('email', '')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.display_name = self.cleaned_data.get('display_name', '')
            profile.phone = self.cleaned_data.get('phone', '')
            if self.cleaned_data.get('profile_photo'):
                profile.profile_photo = self.cleaned_data.get('profile_photo')
            if self.cleaned_data.get('signature_image'):
                profile.signature_image = self.cleaned_data.get('signature_image')
            profile.professional_license = self.cleaned_data.get('professional_license', '')
            profile.linked_patient = None
            profile.can_manage_system = self.cleaned_data.get('can_manage_system', False)
            profile.can_view_sensitive_records = self.cleaned_data.get('can_view_sensitive_records', False)
            profile.save()
            for specialty in self.cleaned_data.get('specialties', []):
                UserSpecialty.objects.get_or_create(user=user, specialty=specialty)
        return user


class UserEditPanelForm(forms.ModelForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES_WITHOUT_PATIENT)
    display_name = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    profile_photo = forms.ImageField(required=False)
    signature_image = forms.ImageField(required=False)
    professional_license = forms.CharField(required=False)
    specialties = forms.ModelMultipleChoiceField(queryset=Specialty.objects.filter(is_active=True), required=False)
    can_manage_system = forms.BooleanField(required=False)
    can_view_sensitive_records = forms.BooleanField(required=False)
    is_active_profile = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        profile = getattr(user, 'profile', None)
        if profile:
            self.fields['role'].initial = profile.role
            self.fields['display_name'].initial = profile.display_name
            self.fields['phone'].initial = profile.phone
            self.fields['profile_photo'].initial = profile.profile_photo
            self.fields['signature_image'].initial = profile.signature_image
            self.fields['professional_license'].initial = profile.professional_license
            self.fields['can_manage_system'].initial = profile.can_manage_system
            self.fields['can_view_sensitive_records'].initial = profile.can_view_sensitive_records
            self.fields['is_active_profile'].initial = profile.is_active_profile
            self.fields['specialties'].initial = [us.specialty_id for us in user.user_specialties.all()]
        for field_name, field in self.fields.items():
            field.label = FIELD_LABELS.get(field_name, field.label)
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', CHECK_INPUT)
            elif isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.setdefault('class', BASE_INPUT + ' min-h-[130px]')
            else:
                field.widget.attrs.setdefault('class', BASE_INPUT)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.display_name = self.cleaned_data.get('display_name', '')
            profile.phone = self.cleaned_data.get('phone', '')
            if self.cleaned_data.get('profile_photo'):
                profile.profile_photo = self.cleaned_data.get('profile_photo')
            if self.cleaned_data.get('signature_image'):
                profile.signature_image = self.cleaned_data.get('signature_image')
            profile.professional_license = self.cleaned_data.get('professional_license', '')
            profile.linked_patient = None
            profile.can_manage_system = self.cleaned_data.get('can_manage_system', False)
            profile.can_view_sensitive_records = self.cleaned_data.get('can_view_sensitive_records', False)
            profile.is_active_profile = self.cleaned_data.get('is_active_profile', True)
            profile.save()
            UserSpecialty.objects.filter(user=user).delete()
            for specialty in self.cleaned_data.get('specialties', []):
                UserSpecialty.objects.get_or_create(user=user, specialty=specialty)
        return user
