from decimal import Decimal, ROUND_HALF_UP
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.http import Http404, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import UserAccountForm, UserCreatePanelForm, UserEditPanelForm, UserSignatureForm
from .models import (
    Admission,
    Appointment,
    ArchivedRecord,
    AuditLog,
    Bed,
    BloodDonationScreening,
    Exam,
    ExamTemplate,
    HealthInsurancePlan,
    InsuranceProvider,
    MedicalDocument,
    MedicalRecord,
    Patient,
    Product,
    PlasterRecord,
    PregnancyFollowUp,
    QuickMessage,
    RoleChangeLog,
    Sale,
    SaleItem,
    Specialty,
    UserProfile,
)
from .module_registry import MODULES
from .permissions import can_access_module, can_manage_admin, can_manage_roles, can_manage_finance, is_medical, is_patient, module_required
from .services import audit, safe_count, safe_queryset


DASHBOARD_CARDS = [
    ('Pacientes', Patient, 'pacientes'),
    ('Consultas', None, 'agenda'),
    ('Atendimentos', MedicalRecord, 'atendimentos'),
    ('Leitos', Bed, 'leitos'),
    ('Internações', Admission, 'internacoes'),
    ('Exames', Exam, 'exames'),
    ('Documentos', MedicalDocument, 'documentos'),
    ('Produtos', Product, 'produtos'),
    ('Convênios', InsuranceProvider, 'convenios'),
    ('Vendas', Sale, 'financeiro'),
]


@login_required
@module_required('dashboard')
def dashboard(request):
    cards = []
    from .models import Appointment
    model_map = {
        'Consultas': Appointment,
    }
    for label, model, slug in DASHBOARD_CARDS:
        model = model or model_map.get(label)
        cards.append({
            'label': label,
            'value': safe_count(request, model) if model else 0,
            'slug': slug,
        })
    bed_free = 0
    bed_busy = 0
    try:
        bed_free = Bed.objects.filter(status='Vago').count()
        bed_busy = Bed.objects.filter(status='Ocupado').count()
    except Exception:
        pass
    recent_logs = safe_queryset(request, AuditLog.objects.select_related('user')[:8])
    return render(request, 'hospital/dashboard.html', {
        'cards': cards,
        'bed_free': bed_free,
        'bed_busy': bed_busy,
        'recent_logs': recent_logs,
    })


def get_module_or_404(slug):
    data = MODULES.get(slug)
    if not data:
        raise Http404('Módulo não encontrado')
    return data


def get_search_queryset(model, query):
    qs = model.objects.all()
    if not query:
        return qs
    q = Q()
    for field in model._meta.fields:
        if field.get_internal_type() in {'CharField', 'TextField', 'EmailField'}:
            q |= Q(**{f'{field.name}__icontains': query})
    return qs.filter(q) if q else qs


def linked_patient_for(user):
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'linked_patient', None) if profile else None


def scoped_queryset_for_user(user, model, qs):
    """Aplica autorização de dados no backend.
    Paciente vê somente registros vinculados ao próprio paciente.
    Médicos/residentes veem preferencialmente registros em que participaram.
    Administradores e direção mantêm visão ampla.
    """
    if not user.is_authenticated:
        return qs.none()
    if can_manage_admin(user) or getattr(user, 'is_superuser', False):
        return qs
    patient = linked_patient_for(user)
    role = getattr(getattr(user, 'profile', None), 'role', '')
    if is_patient(user):
        if model is Patient:
            return qs.filter(pk=getattr(patient, 'pk', None)) if patient else qs.none()
        if model is Appointment and patient:
            return qs.filter(patient=patient)
        if model is MedicalRecord and patient:
            return qs.filter(patient=patient).exclude(status__in=['Rascunho', 'Aguardando aprovação'])
        if model is Exam and patient:
            return qs.filter(patient=patient).filter(status__in=['Finalizado', 'Entregue ao paciente'])
        if model is MedicalDocument and patient:
            return qs.filter(patient=patient).exclude(status='Rascunho')
        if model is PlasterRecord and patient:
            return qs.filter(patient=patient)
        if model is PregnancyFollowUp and patient:
            return qs.filter(patient=patient)
        if model is HealthInsurancePlan and patient:
            return qs.filter(Q(titular_patient=patient) | Q(dependents=patient)).distinct()
        return qs.none()
    if model is QuickMessage:
        return qs.filter(created_by=user)
    if is_medical(user):
        if model is Patient:
            return qs.filter(
                Q(appointments__doctor=user) | Q(medical_records__doctor=user) | Q(exams__requesting_doctor=user) |
                Q(documents__requesting_doctor=user) | Q(admissions__doctor=user) | Q(plaster_records__doctor=user)
            ).distinct()
        if model is Appointment:
            return qs.filter(Q(doctor=user) | Q(status__in=['Agendada', 'Confirmada', 'Em atendimento']))
        if model is MedicalRecord:
            return qs.filter(Q(doctor=user) | Q(student_author=user) | Q(supervisor=user))
        if model is Exam:
            return qs.filter(Q(requesting_doctor=user) | Q(status__in=['Solicitado', 'Em análise', 'Finalizado']))
        if model is MedicalDocument:
            return qs.filter(Q(requesting_doctor=user) | Q(status__in=['Emitido', 'Entregue']))
        if model in {Admission, Bed, PlasterRecord, PregnancyFollowUp, BloodDonationScreening}:
            return qs
    if role == 'financeiro' or can_manage_finance(user):
        if model in {Sale, Product, InsuranceProvider, HealthInsurancePlan, Patient}:
            return qs
    if role in {'recepcao'}:
        if model in {Patient, Appointment}:
            return qs
    return qs


def object_allowed_for_user(user, model, obj):
    return scoped_queryset_for_user(user, model, model.objects.filter(pk=obj.pk)).exists()


def render_exam_template_text(template, exam=None, patient=None, doctor=None):
    """Renderiza placeholders simples do modelo mantendo o texto editável pelo médico."""
    if not template:
        return ''
    today = timezone.localdate().strftime('%d/%m/%Y')
    replacements = {
        '{hospital}': 'Centro Médico SHINE',
        '{data}': today,
        '{paciente}': str(patient or getattr(exam, 'patient', '') or '________________________________'),
        '{medico}': str(doctor or getattr(exam, 'requesting_doctor', '') or '________________________________'),
        '{exame}': template.exam_type or template.name,
        '{material}': template.sample_material or 'Conforme protocolo do exame',
        '{indicacao}': template.clinical_indication or 'Avaliação clínica conforme solicitação médica',
    }
    content = template.template_content or ''
    for key, value in replacements.items():
        content = content.replace(key, value)
    return content


def exam_template_payload():
    payload = {}
    for template in ExamTemplate.objects.filter(is_active=True).order_by('category', 'name'):
        payload[str(template.pk)] = {
            'name': template.name,
            'category': template.category,
            'exam_type': template.exam_type,
            'clinical_indication': template.clinical_indication,
            'sample_material': template.sample_material,
            'report': template.template_content,
            'conclusion': template.conclusion_template,
            'recommendations': template.recommendations,
            'preparation': template.preparation,
        }
    return json.dumps(payload, cls=DjangoJSONEncoder, ensure_ascii=False)

MONEY_Q = Decimal('0.01')


def money(value):
    return Decimal(value or 0).quantize(MONEY_Q, rounding=ROUND_HALF_UP)


def active_health_plan_for_patient(patient):
    if not patient:
        return None
    today = timezone.localdate()
    return HealthInsurancePlan.objects.filter(
        Q(titular_patient=patient) | Q(dependents=patient),
        status='Ativo',
    ).filter(Q(due_date__isnull=True) | Q(due_date__gte=today)).order_by('-discount_percent', '-updated_at').first()


def automatic_discount_for_patient(patient):
    """Retorna desconto automático por plano familiar/individual ativo e/ou empresa vinculada ativa."""
    plan = active_health_plan_for_patient(patient)
    company = getattr(patient, 'company_provider', None) if patient else None
    plan_percent = Decimal('0.00')
    company_percent = Decimal('0.00')
    sources = []
    if plan and plan.discount_percent:
        plan_percent = Decimal(plan.discount_percent)
        sources.append(f'Plano de saúde {plan.plan_type}: {plan_percent}%')
    if company and company.is_active and company.default_discount_percent:
        company_percent = Decimal(company.default_discount_percent)
        sources.append(f'Convênio empresarial {company.name}: {company_percent}%')
    # Soma os benefícios ativos e limita para impedir valor negativo por erro de cadastro.
    total = min(plan_percent + company_percent, Decimal('90.00'))
    return {
        'plan': plan,
        'company': company if company and company.is_active else None,
        'plan_percent': plan_percent,
        'company_percent': company_percent,
        'total_percent': total,
        'source': ' + '.join(sources) if sources else 'Sem desconto ativo',
    }


def build_receipt_text(sale):
    lines = [
        'Centro Médico SHINE',
        f'Recibo financeiro #{sale.pk}',
        f'Data: {timezone.localtime(sale.created_at).strftime("%d/%m/%Y %H:%M") if sale.created_at else timezone.localtime().strftime("%d/%m/%Y %H:%M")}',
        f'Paciente: {sale.patient or "Não informado"}',
        f'Operador: {sale.operator or "Sistema"}',
        '',
        'Itens:',
    ]
    for item in sale.items.all():
        lines.append(f'- {item.quantity}x {item.product_name} | R$ {money(item.price)} | Total R$ {money(item.total)}')
    lines += [
        '',
        f'Subtotal: R$ {money(sale.subtotal)}',
        f'Desconto: {sale.discount_percent}% | R$ {money(sale.discount_amount)}',
        f'Origem do desconto: {sale.discount_source or "Sem desconto"}',
        f'TOTAL: R$ {money(sale.total)}',
        '',
        'Comprovante gerado pelo sistema. Nenhum upload de comprovante é necessário.',
        'Obrigado pela confiança no Centro Médico SHINE.',
    ]
    return '\n'.join(lines)


def finance_cashier(request):
    if not can_access_module(request.user, 'financeiro'):
        messages.error(request, 'Você não tem permissão para acessar o financeiro.')
        return redirect('dashboard')
    products = list(Product.objects.filter(is_active=True).order_by('category', 'name'))
    patients = list(Patient.objects.filter(status='Ativo').order_by('full_name'))

    if request.method == 'POST':
        patient = None
        patient_id = request.POST.get('patient')
        if patient_id:
            patient = get_object_or_404(Patient, pk=patient_id)
        selected_items = []
        subtotal = Decimal('0.00')
        discountable_subtotal = Decimal('0.00')
        for product in products:
            raw_qty = request.POST.get(f'qty_{product.pk}', '0') or '0'
            try:
                qty = int(raw_qty)
            except ValueError:
                qty = 0
            if qty <= 0:
                continue
            if product.stock and qty > product.stock:
                messages.error(request, f'Estoque insuficiente para {product.name}. Disponível: {product.stock}.')
                return redirect('module_list', slug='financeiro')
            line_total = money(product.price) * qty
            subtotal += line_total
            if product.discount_allowed:
                discountable_subtotal += line_total
            selected_items.append((product, qty, money(product.price)))

        if not selected_items:
            messages.error(request, 'Selecione pelo menos um produto ou serviço para finalizar a venda.')
            return redirect('module_list', slug='financeiro')

        discount_info = automatic_discount_for_patient(patient)
        discount_percent = discount_info['total_percent']
        discount_amount = money(discountable_subtotal * discount_percent / Decimal('100'))
        total = money(subtotal - discount_amount)
        sale = Sale.objects.create(
            patient=patient,
            operator=request.user,
            provider=discount_info['company'],
            original_total=money(subtotal),
            subtotal=money(subtotal),
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            discount_source=discount_info['source'],
            discount_applied_by=request.user if discount_amount > 0 else None,
            total=total,
            status='Finalizada',
        )
        for product, qty, price in selected_items:
            SaleItem.objects.create(sale=sale, product=product, product_name=product.name, price=price, quantity=qty)
            if product.stock:
                product.stock = max(product.stock - qty, 0)
                product.save(update_fields=['stock', 'updated_at'])
        sale.receipt_text = build_receipt_text(sale)
        sale.save(update_fields=['receipt_text', 'updated_at'])
        audit(request, 'create', module='financeiro', obj=sale, after={'total': str(sale.total), 'discount': str(sale.discount_percent), 'source': sale.discount_source})
        messages.success(request, f'Venda #{sale.pk} finalizada. Recibo disponível para download.')
        return redirect('module_list', slug='financeiro')

    discount_map = {}
    for patient in patients:
        info = automatic_discount_for_patient(patient)
        discount_map[str(patient.pk)] = {
            'total_percent': str(info['total_percent']),
            'plan_percent': str(info['plan_percent']),
            'company_percent': str(info['company_percent']),
            'source': info['source'],
            'company_name': info['company'].name if info['company'] else '',
            'plan_name': info['plan'].plan_type if info['plan'] else '',
        }
    recent_sales = safe_queryset(request, Sale.objects.select_related('patient', 'operator', 'provider').prefetch_related('items')[:30])
    return render(request, 'hospital/finance_cashier.html', {
        'slug': 'financeiro',
        'module': MODULES['financeiro'],
        'products': products,
        'patients': patients,
        'recent_sales': recent_sales,
        'discount_map_json': json.dumps(discount_map, ensure_ascii=False),
    })


def quick_messages_page(request):
    if not can_access_module(request.user, 'mensagens-rapidas'):
        messages.error(request, 'Você não tem permissão para acessar mensagens rápidas.')
        return redirect('dashboard')
    if request.method == 'POST':
        action = request.POST.get('action', 'create')
        message_id = request.POST.get('message_id')
        if action in {'delete', 'favorite'} and message_id:
            obj = get_object_or_404(scoped_queryset_for_user(request.user, QuickMessage, QuickMessage.objects.all()), pk=message_id)
            if action == 'delete':
                obj.delete()
                messages.success(request, 'Mensagem apagada.')
            else:
                obj.is_favorite = not obj.is_favorite
                obj.save(update_fields=['is_favorite', 'updated_at'])
                messages.success(request, 'Favorito atualizado.')
            return redirect('module_list', slug='mensagens-rapidas')
        text = (request.POST.get('message') or '').strip()
        if not text:
            messages.error(request, 'Digite uma mensagem antes de salvar o cartão.')
            return redirect('module_list', slug='mensagens-rapidas')
        QuickMessage.objects.create(
            prefix=(request.POST.get('prefix') or '').strip(),
            message=text,
            initial_emojis=(request.POST.get('initial_emojis') or '').strip(),
            final_emojis=(request.POST.get('final_emojis') or '').strip(),
            category=request.POST.get('category') or 'Geral',
            is_favorite=bool(request.POST.get('is_favorite')),
            created_by=request.user,
        )
        messages.success(request, 'Cartão de mensagem salvo com sucesso.')
        return redirect('module_list', slug='mensagens-rapidas')

    messages_qs = scoped_queryset_for_user(request.user, QuickMessage, QuickMessage.objects.all())
    return render(request, 'hospital/quick_messages.html', {
        'slug': 'mensagens-rapidas',
        'module': MODULES['mensagens-rapidas'],
        'items': safe_queryset(request, messages_qs[:200]),
        'categories': QuickMessage.CATEGORY_CHOICES,
        'emoji_options': ['✅', '🚑', '💉', '❤️', '🚨', '🏃', '🏥', '🩺', '📍', '⏳', '⚠️', '❓', '👍'],
    })



@login_required
def module_list(request, slug):
    if not can_access_module(request.user, slug):
        messages.error(request, 'Você não tem permissão para acessar este módulo.')
        return redirect('dashboard')
    if slug == 'financeiro':
        return finance_cashier(request)
    if slug == 'mensagens-rapidas':
        return quick_messages_page(request)
    module = get_module_or_404(slug)
    model = module['model']
    query = request.GET.get('q', '').strip()
    base_qs = scoped_queryset_for_user(request.user, model, get_search_queryset(model, query))
    qs = base_qs.order_by('-id')[:250]
    items = safe_queryset(request, qs)
    extra = {}
    if slug == 'exames':
        extra['exam_templates'] = safe_queryset(request, ExamTemplate.objects.filter(is_active=True).order_by('category', 'name')[:80])
    return render(request, 'hospital/module_list.html', {
        'slug': slug,
        'module': module,
        'items': items,
        'columns': module.get('columns', []),
        'query': query,
        **extra,
    })


@login_required
def module_create(request, slug):
    if not can_access_module(request.user, slug) or is_patient(request.user):
        messages.error(request, 'Você não tem permissão para criar neste módulo.')
        return redirect('dashboard')
    if slug in {'financeiro', 'mensagens-rapidas'}:
        return redirect('module_list', slug=slug)
    module = get_module_or_404(slug)
    form_class = module['form']

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                if hasattr(obj, 'created_by') and not obj.created_by_id:
                    obj.created_by = request.user
                if hasattr(obj, 'operator') and not obj.operator_id:
                    obj.operator = request.user
                if slug == 'exames':
                    if is_medical(request.user) and not obj.requesting_doctor_id:
                        obj.requesting_doctor = request.user
                    if obj.template and not obj.report:
                        obj.report = render_exam_template_text(obj.template, obj, obj.patient, obj.requesting_doctor or request.user)
                    if form.cleaned_data.get('sign_now'):
                        if not getattr(getattr(request.user, 'profile', None), 'signature_image', None):
                            messages.error(request, 'Cadastre sua assinatura médica no menu do perfil antes de assinar exames.')
                            return redirect('profile_signature')
                        obj.signed_by = request.user
                        obj.signed_at = timezone.now()
                        obj.status = 'Finalizado'
                if hasattr(obj, 'discount_applied_by') and getattr(obj, 'discount_percent', 0) and not obj.discount_applied_by_id:
                    obj.discount_applied_by = request.user
                obj.save()
                if hasattr(form, 'save_m2m'):
                    form.save_m2m()
                audit(request, 'create', module=slug, obj=obj)
                messages.success(request, 'Registro salvo com sucesso.')
                return redirect('module_list', slug=slug)
            except Exception as exc:
                audit(request, 'error', module=slug, message=str(exc))
                messages.error(request, 'Não foi possível salvar. Verifique o banco e tente novamente.')
    else:
        initial = {}
        if slug == 'exames':
            template_id = request.GET.get('modelo')
            if template_id:
                template = ExamTemplate.objects.filter(pk=template_id, is_active=True).first()
                if template:
                    initial.update({
                        'template': template,
                        'exam_type': template.exam_type,
                        'clinical_indication': template.clinical_indication,
                        'sample_material': template.sample_material,
                        'report': render_exam_template_text(template, doctor=request.user),
                        'conclusion': template.conclusion_template,
                        'recommendations': template.recommendations,
                    })
            if is_medical(request.user):
                initial.setdefault('requesting_doctor', request.user)
        form = form_class(initial=initial)

    template_name = 'hospital/exam_form.html' if slug == 'exames' else 'hospital/module_form.html'
    context = {'slug': slug, 'module': module, 'form': form, 'mode': 'create'}
    if slug == 'exames':
        context['template_payload_json'] = exam_template_payload()
        context['doctor_signature'] = getattr(getattr(request.user, 'profile', None), 'signature_image', None)
    return render(request, template_name, context)


@login_required
def module_edit(request, slug, pk):
    if not can_access_module(request.user, slug):
        messages.error(request, 'Você não tem permissão para editar este módulo.')
        return redirect('dashboard')
    module = get_module_or_404(slug)
    model = module['model']
    obj = get_object_or_404(model, pk=pk)
    if not object_allowed_for_user(request.user, model, obj):
        messages.error(request, 'Você não tem permissão para acessar este registro.')
        return redirect('dashboard')
    form_class = module['form']
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            before = {field: str(getattr(obj, field, '')) for field in module.get('columns', [])}
            try:
                saved = form.save(commit=False)
                if slug == 'exames':
                    if saved.template and not saved.report:
                        saved.report = render_exam_template_text(saved.template, saved, saved.patient, saved.requesting_doctor or request.user)
                    if form.cleaned_data.get('sign_now'):
                        if not getattr(getattr(request.user, 'profile', None), 'signature_image', None):
                            messages.error(request, 'Cadastre sua assinatura médica no menu do perfil antes de assinar exames.')
                            return redirect('profile_signature')
                        saved.signed_by = request.user
                        saved.signed_at = timezone.now()
                        saved.status = 'Finalizado'
                saved.save()
                if hasattr(form, 'save_m2m'):
                    form.save_m2m()
                after = {field: str(getattr(saved, field, '')) for field in module.get('columns', [])}
                audit(request, 'update', module=slug, obj=saved, before=before, after=after)
                messages.success(request, 'Registro atualizado com sucesso.')
                return redirect('module_list', slug=slug)
            except Exception as exc:
                audit(request, 'error', module=slug, message=str(exc))
                messages.error(request, 'Não foi possível atualizar. Verifique o banco e tente novamente.')
    else:
        form = form_class(instance=obj)
    template_name = 'hospital/exam_form.html' if slug == 'exames' else 'hospital/module_form.html'
    context = {'slug': slug, 'module': module, 'form': form, 'mode': 'edit', 'object': obj}
    if slug == 'exames':
        context['template_payload_json'] = exam_template_payload()
        context['doctor_signature'] = getattr(getattr(request.user, 'profile', None), 'signature_image', None)
    return render(request, template_name, context)


@login_required
@require_POST
def module_archive(request, slug, pk):
    if not can_access_module(request.user, slug):
        messages.error(request, 'Você não tem permissão para arquivar.')
        return redirect('dashboard')
    module = get_module_or_404(slug)
    model = module['model']
    obj = get_object_or_404(model, pk=pk)
    if not object_allowed_for_user(request.user, model, obj):
        messages.error(request, 'Você não tem permissão para arquivar este registro.')
        return redirect('dashboard')
    try:
        if hasattr(obj, 'status'):
            obj.status = 'Arquivado'
            obj.save(update_fields=['status', 'updated_at'] if hasattr(obj, 'updated_at') else ['status'])
        ArchivedRecord.objects.create(module=slug, object_label=str(obj), object_id=str(obj.pk), archived_by=request.user)
        audit(request, 'archive', module=slug, obj=obj)
        messages.success(request, 'Registro arquivado com sucesso.')
    except Exception as exc:
        audit(request, 'error', module=slug, obj=obj, message=str(exc))
        messages.error(request, 'Não foi possível arquivar este registro.')
    return redirect('module_list', slug=slug)


@login_required
@require_POST
def module_delete(request, slug, pk):
    if not can_manage_admin(request.user):
        messages.error(request, 'Somente administradores podem excluir definitivamente.')
        return redirect('module_list', slug=slug)
    module = get_module_or_404(slug)
    model = module['model']
    obj = get_object_or_404(model, pk=pk)
    label = str(obj)
    try:
        obj.delete()
        audit(request, 'delete', module=slug, message=label)
        messages.success(request, 'Registro excluído definitivamente.')
    except Exception as exc:
        audit(request, 'error', module=slug, message=str(exc))
        messages.error(request, 'Não foi possível excluir este registro.')
    return redirect('module_list', slug=slug)


@login_required
@module_required('pacientes')
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if is_patient(request.user) and linked_patient_for(request.user) != patient:
        messages.error(request, 'Você não tem permissão para ver dados de outro paciente.')
        return redirect('patient_portal')
    history = {
        'Atendimentos': safe_queryset(request, patient.medical_records.select_related('doctor', 'specialty')[:20]),
        'Consultas': safe_queryset(request, patient.appointments.select_related('doctor', 'specialty')[:20]),
        'Exames': safe_queryset(request, patient.exams.select_related('requesting_doctor')[:20]),
        'Documentos': safe_queryset(request, patient.documents.select_related('requesting_doctor')[:20]),
        'Internações': safe_queryset(request, patient.admissions.select_related('doctor', 'bed')[:20]),
        'Gesso': safe_queryset(request, patient.plaster_records.select_related('doctor')[:20]),
        'Gestação': safe_queryset(request, patient.pregnancies.select_related('doctor')[:20]),
        'Doação de sangue': safe_queryset(request, patient.blood_donations.select_related('doctor')[:20]),
    }
    return render(request, 'hospital/patient_detail.html', {'patient': patient, 'history': history})


@login_required
@module_required('arquivados')
def archive_list(request):
    items = safe_queryset(request, ArchivedRecord.objects.select_related('archived_by')[:300])
    return render(request, 'hospital/archive.html', {'items': items})


@login_required
@module_required('relatorios')
def reports(request):
    counts = {
        'Pacientes': safe_count(request, Patient),
        'Leitos': safe_count(request, Bed),
        'Internações': safe_count(request, Admission),
        'Exames': safe_count(request, Exam),
        'Documentos': safe_count(request, MedicalDocument),
        'Planos': safe_count(request, HealthInsurancePlan),
        'Produtos': safe_count(request, Product),
        'Convênios': safe_count(request, InsuranceProvider),
        'Mensagens': safe_count(request, QuickMessage),
        'Doações': safe_count(request, BloodDonationScreening),
        'Gesso': safe_count(request, PlasterRecord),
        'Gestações': safe_count(request, PregnancyFollowUp),
    }
    revenue = 0
    try:
        revenue = Sale.objects.aggregate(total=Sum('total'))['total'] or 0
    except Exception:
        pass
    return render(request, 'hospital/reports.html', {'counts': counts, 'revenue': revenue})


@login_required
@module_required('administracao')
def admin_panel(request):
    if not (can_manage_admin(request.user) or can_manage_roles(request.user)):
        messages.error(request, 'Você não tem permissão administrativa.')
        return redirect('dashboard')
    users = safe_queryset(request, User.objects.select_related('profile').order_by('username')[:200])
    specialties = safe_queryset(request, Specialty.objects.all())
    products = safe_queryset(request, Product.objects.all()[:20])
    providers = safe_queryset(request, InsuranceProvider.objects.all()[:20])
    role_logs = safe_queryset(request, RoleChangeLog.objects.select_related('changed_by', 'changed_user')[:20])
    logs = safe_queryset(request, AuditLog.objects.select_related('user')[:30])
    return render(request, 'hospital/admin_panel.html', {'users': users, 'specialties': specialties, 'products': products, 'providers': providers, 'role_logs': role_logs, 'logs': logs})


@login_required
@module_required('administracao')
def user_create(request):
    if not (can_manage_admin(request.user) or can_manage_roles(request.user)):
        messages.error(request, 'Você não tem permissão para criar usuários.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreatePanelForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            audit(request, 'create', module='usuários', obj=user)
            messages.success(request, 'Usuário criado com sucesso.')
            return redirect('admin_panel')
    else:
        form = UserCreatePanelForm()
    return render(request, 'hospital/user_form.html', {'form': form, 'title': 'Criar usuário'})


@login_required
@module_required('administracao')
def user_edit(request, pk):
    if not (can_manage_admin(request.user) or can_manage_roles(request.user)):
        messages.error(request, 'Você não tem permissão para editar usuários.')
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditPanelForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            previous_role = getattr(user.profile, 'role', '') if hasattr(user, 'profile') else ''
            requested_role = form.cleaned_data.get('role')
            if user == request.user and requested_role != previous_role:
                messages.error(request, 'Você não pode alterar o próprio cargo.')
                return redirect('user_edit', pk=pk)
            if not can_manage_admin(request.user) and requested_role in {'super_admin', 'admin', 'presidente_hospital', 'diretor', 'vice_diretor'}:
                messages.error(request, 'Seu cargo não permite promover para cargos de direção ou administração máxima.')
                return redirect('user_edit', pk=pk)
            saved = form.save()
            new_role = getattr(saved.profile, 'role', '') if hasattr(saved, 'profile') else ''
            if previous_role != new_role:
                RoleChangeLog.objects.create(changed_by=request.user, changed_user=saved, previous_role=previous_role, new_role=new_role, reason='Alterado no painel administrativo')
                audit(request, 'role_change', module='cargos', obj=saved, before={'role': previous_role}, after={'role': new_role})
            audit(request, 'update', module='usuários', obj=saved)
            messages.success(request, 'Usuário atualizado com sucesso.')
            return redirect('admin_panel')
    else:
        form = UserEditPanelForm(instance=user)
    return render(request, 'hospital/user_form.html', {'form': form, 'title': 'Editar usuário'})


@login_required
@module_required('portal-paciente')
def patient_portal(request):
    profile = getattr(request.user, 'profile', None)
    patient = getattr(profile, 'linked_patient', None)
    if not patient:
        messages.error(request, 'Sua conta ainda não esta vinculada a um paciente.')
        return render(request, 'hospital/patient_portal.html', {'patient': None})
    context = {
        'patient': patient,
        'next_appointment': safe_queryset(request, patient.appointments.filter(status__in=['Agendada', 'Confirmada']).order_by('scheduled_at')[:1]),
        'appointments': safe_queryset(request, patient.appointments.all()[:20]),
        'exams': safe_queryset(request, patient.exams.filter(status__in=['Finalizado', 'Entregue ao paciente'])[:20]),
        'documents': safe_queryset(request, patient.documents.exclude(status='Rascunho')[:20]),
        'records': safe_queryset(request, patient.medical_records.exclude(status__in=['Rascunho', 'Aguardando aprovação'])[:20]),
        'plaster_records': safe_queryset(request, patient.plaster_records.all()[:20]),
        'plans': safe_queryset(request, patient.insurance_plans.all()[:20]),
    }
    return render(request, 'hospital/patient_portal.html', context)


@login_required
def profile_account(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserAccountForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            saved = form.save()
            audit(
                request,
                'update',
                module='perfil',
                obj=request.user,
                after={
                    'display_name': saved.display_name,
                    'phone': saved.phone,
                    'profile_photo': bool(saved.profile_photo),
                },
            )
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('profile_account')
    else:
        form = UserAccountForm(instance=profile)
    return render(request, 'hospital/profile_account.html', {'form': form, 'profile': profile})


@login_required
def profile_signature(request):
    if not (is_medical(request.user) or can_manage_admin(request.user) or getattr(request.user, 'is_staff', False)):
        messages.error(request, 'Apenas médicos, equipes autorizadas e administradores podem cadastrar assinatura profissional.')
        return redirect('dashboard')
    profile = getattr(request.user, 'profile', None)
    if not profile:
        messages.error(request, 'Perfil não encontrado.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserSignatureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            saved = form.save(commit=False)
            if request.FILES.get('signature_image'):
                saved.signature_registered_at = timezone.now()
            saved.save()
            audit(request, 'update', module='assinatura-medica', obj=request.user, after={'professional_license': saved.professional_license})
            messages.success(request, 'Assinatura médica atualizada com sucesso.')
            return redirect('profile_signature')
    else:
        form = UserSignatureForm(instance=profile)
    return render(request, 'hospital/profile_signature.html', {'form': form, 'profile': profile})


@login_required
@module_required('exames')
def exam_template_library(request):
    categories = {}
    for template in ExamTemplate.objects.filter(is_active=True).order_by('category', 'name'):
        categories.setdefault(template.category, []).append(template)
    return render(request, 'hospital/exam_template_library.html', {'categories': categories, 'slug': 'exames'})


@login_required
@module_required('exames')
def exam_print(request, pk):
    exam = get_object_or_404(Exam.objects.select_related('patient', 'requesting_doctor', 'signed_by', 'template'), pk=pk)
    if not object_allowed_for_user(request.user, Exam, exam):
        messages.error(request, 'Você não tem permissão para visualizar este exame.')
        return redirect('dashboard')
    signature_profile = getattr(exam.signed_by, 'profile', None) if exam.signed_by else getattr(exam.requesting_doctor, 'profile', None)
    return render(request, 'hospital/exam_report_print.html', {'exam': exam, 'signature_profile': signature_profile})


@login_required
def sale_receipt_download(request, pk):
    sale = get_object_or_404(Sale.objects.select_related('patient', 'operator', 'provider').prefetch_related('items'), pk=pk)
    if not (can_access_module(request.user, 'financeiro') or (is_patient(request.user) and linked_patient_for(request.user) == sale.patient)):
        messages.error(request, 'Você não tem permissão para baixar este recibo.')
        return redirect('dashboard')
    content = sale.receipt_text or build_receipt_text(sale)
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="recibo-shine-{sale.pk}.txt"'
    return response


def discord_login_start(request):
    messages.info(request, 'Login por Discord preparado, mas ainda não ativado neste ambiente de desenvolvimento.')
    return redirect('login')

def root_redirect(request):
    return render(request, 'hospital/landing.html')
