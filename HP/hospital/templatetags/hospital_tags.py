from django import template

register = template.Library()

FIELD_LABELS = {
    'full_name': 'Nome completo',
    'document': 'Documento',
    'phone': 'Telefone',
    'email': 'E-mail',
    'status': 'Situação',
    'patient': 'Paciente',
    'doctor': 'Médico',
    'requesting_doctor': 'Médico solicitante',
    'responsible_doctor': 'Médico responsável',
    'specialty': 'Especialidade',
    'scheduled_at': 'Data e hora',
    'attendance_date': 'Data do atendimento',
    'name': 'Nome',
    'ward': 'Ala / setor',
    'current_patient': 'Paciente atual',
    'bed': 'Leito',
    'entry_date': 'Entrada',
    'expected_discharge': 'Previsão de alta',
    'exam_type': 'Tipo de exame',
    'issue_date': 'Emissão',
    'document_type': 'Tipo de documento',
    'collection_date': 'Data da coleta',
    'blood_type': 'Tipo sanguíneo',
    'rh_factor': 'Fator RH',
    'result': 'Resultado',
    'start_date': 'Início',
    'real_days': 'Dias reais',
    'consultation_count': 'Consultas',
    'body_part': 'Parte do corpo',
    'placement_date': 'Colocação',
    'removal_date': 'Retirada',
    'plan_type': 'Tipo de plano',
    'titular_patient': 'Paciente titular',
    'sale_date': 'Venda',
    'due_date': 'Vencimento',
    'value': 'Valor',
    'operator': 'Operador',
    'subtotal': 'Subtotal',
    'discount_percent': 'Desconto',
    'total': 'Total',
    'prefix': 'Prefixo',
    'message': 'Mensagem',
    'category': 'Categoria',
    'created_by': 'Criado por',
    'is_favorite': 'Favorito',
    'slug': 'Slug',
    'is_active': 'Ativo',
    'key': 'Chave',
    'provider': 'Convênio',
    'default_discount_percent': 'Desconto padrão',
    'price': 'Preço',
    'stock': 'Estoque',
    'discount_allowed': 'Desconto permitido',
    'original_total': 'Valor original',
    'discount_amount': 'Valor desconto',
    'changed_user': 'Usuário alterado',
    'previous_role': 'Cargo anterior',
    'new_role': 'Novo cargo',
    'changed_by': 'Alterado por',
    'is_public': 'Público',
}


@register.filter
def attr(obj, name):
    try:
        value = getattr(obj, name)
        if callable(value):
            value = value()
        return value
    except Exception:
        return ''


@register.filter
def field_label(obj, name):
    if name in FIELD_LABELS:
        return FIELD_LABELS[name]
    try:
        return obj._meta.get_field(name).verbose_name.title()
    except Exception:
        return name.replace('_', ' ').title()


@register.filter
def badge_class(value):
    text = str(value).lower()
    if any(x in text for x in ['ativo', 'apto', 'finalizado', 'vago', 'emitido', 'confirmada']):
        return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
    if any(x in text for x in ['cancel', 'inapto', 'atrasado', 'bloqueado', 'manutenção']):
        return 'bg-red-500/10 text-red-300 border-red-500/30'
    if any(x in text for x in ['pendente', 'rascunho', 'aguardando', 'em análise', 'em analise', 'reservado']):
        return 'bg-amber-500/10 text-amber-300 border-amber-500/30'
    if any(x in text for x in ['arquivado', 'alta', 'entregue']):
        return 'bg-slate-500/10 text-slate-300 border-slate-500/30'
    return 'bg-sky-500/10 text-sky-300 border-sky-500/30'
