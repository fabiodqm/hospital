# AUDITORIA FINAL - Centro Médico SHINE

## Plano técnico aplicado

1. Preservar o Django existente, banco SQLite/Supabase e módulos já funcionais.
2. Reforçar RBAC no backend, não apenas no front-end.
3. Separar áreas de Paciente, Médico, Enfermagem, Financeiro, Direção e Admin.
4. Melhorar financeiro com produtos, imagens, convênios e descontos.
5. Melhorar UX com sidebar profissional, dropdown premium, cards com profundidade, busca e estados vazios.
6. Preparar Discord OAuth por variáveis de ambiente, sem ativar o bloqueio obrigatório em desenvolvimento.

## Fragilidades encontradas

- Pacientes poderiam receber links diretos para módulos sem isolamento detalhado por objeto.
- Mensagens rápidas não estavam isoladas por médico.
- Financeiro não tinha cadastro profissional de produtos/imagens/convênios.
- Não havia rate limit simples para login.
- Não havia middleware dedicado para headers HTTP seguros.
- Cargos de direção, chefias, residência e enfermagem não estavam representados de forma completa.
- Alterações de cargo não tinham log próprio.

## Vulnerabilidades corrigidas ou reduzidas

- Autorização por módulo reforçada no backend.
- Escopo de dados por usuário implementado em `scoped_queryset_for_user`.
- Paciente passa a visualizar somente dados do próprio `linked_patient`.
- Médico vê preferencialmente registros em que participou ou módulos clínicos operacionais.
- Mensagens rápidas passam a ser filtradas por `created_by` para usuários não-admin.
- Alteração de cargo gera `RoleChangeLog` e `AuditLog`.
- Bloqueio contra autopromoção no painel de usuários.
- Rate limit simples no login via `LoginRateLimitMiddleware`.
- Headers de segurança via `SecurityHeadersMiddleware`.
- Uploads com limite de tamanho e validação de extensão para imagens/arquivos.
- Variáveis sensíveis mantidas no `.env`.

## Pontos que ainda precisam de atenção para produção

- Ativar HTTPS e cookies `Secure` em produção.
- Ativar Discord OAuth obrigatório e validação de guild antes de liberar acesso.
- Usar PostgreSQL/Supabase em produção, não SQLite.
- Configurar storage seguro para imagens e anexos.
- Configurar backup, logs centralizados e monitoramento.
- Revisar LGPD/termos médicos antes de uso real.
- Criar testes automatizados de regressão e autorização.
- Configurar WAF/firewall/reverse proxy com Nginx ou Cloudflare.

## Arquivos principais alterados/criados

- `hospital/models.py`
- `hospital/forms.py`
- `hospital/views.py`
- `hospital/permissions.py`
- `hospital/module_registry.py`
- `hospital/middleware.py`
- `hospital/management/commands/seed_base_data.py`
- `hospital/migrations/0002_security_rbac_finance.py`
- `templates/base.html`
- `templates/hospital/module_list.html`
- `templates/hospital/admin_panel.html`
- `templates/hospital/patient_portal.html`
- `static/css/app.css`
- `.env.example`
- `AUDITORIA_FINAL.md`

## Contas de teste criadas automaticamente

Após rodar `START.bat` ou `python manage.py seed_base_data`:

- Admin: `admin` / `admin123456`
- Médico: `medico` / `medico123456`
- Paciente: `paciente` / `paciente123456`

## Como testar permissões

### Admin

1. Entrar com `admin / admin123456`.
2. Acessar `/dashboard/`.
3. Acessar Administração, Produtos, Convênios, Financeiro, Cargos e Configurações.
4. Editar um usuário e verificar criação de log de alteração de cargo.

### Médico

1. Entrar com `medico / medico123456`.
2. Ver dashboard, agenda, pacientes relacionados, prontuário, exames, documentos e mensagens rápidas.
3. Criar mensagem rápida.
4. Confirmar que a mensagem pertence ao médico logado.
5. Confirmar que não tem controle total do painel admin.

### Paciente

1. Entrar com `paciente / paciente123456`.
2. Confirmar redirecionamento/uso do Portal do Paciente.
3. Ver consultas, exames, documentos e histórico do próprio paciente vinculado.
4. Tentar acessar `/pacientes/` ou registros de outros pacientes e confirmar bloqueio.

### Financeiro

1. Usar um usuário com cargo Financeiro.
2. Criar produtos com preço, imagem, categoria e estoque.
3. Criar convênio com desconto padrão.
4. Criar venda vinculando paciente/convênio e conferir valores de desconto.

## Como validar isolamento de dados

- Crie dois pacientes.
- Vincule o usuário `paciente` apenas ao Paciente A.
- Acesse o portal e confirme que só aparecem dados do Paciente A.
- Tente abrir a URL de detalhe do Paciente B.
- O sistema deve bloquear e retornar para o portal.

## Como validar que médico não acessa admin total

- Entrar como `medico`.
- Tentar acessar `/administracao/`.
- A permissão administrativa total deve ser negada, salvo cargos de direção configurados.

## Como validar que Admin controla tudo

- Entrar como `admin`.
- Acessar todos os módulos.
- Criar/editar usuários.
- Criar produtos, convênios, vendas, mensagens, pacientes e logs.

## Discord OAuth

A estrutura está preparada por variáveis:

- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `DISCORD_REDIRECT_URI`
- `DISCORD_GUILD_ID`
- `DISCORD_OAUTH_ENABLED`

Neste pacote o fluxo obrigatório ainda fica desativado por padrão para facilitar testes locais.

## Atualização financeiro/mensagens - 22/05/2026

Melhorias aplicadas nesta versão:

- O módulo **Financeiro e Caixa** agora usa uma tela própria de caixa, com produtos cadastrados aparecendo como cards vendáveis.
- O comprovante deixou de ser enviado por upload: cada venda gera um **recibo para download** em texto.
- O desconto agora é calculado automaticamente no backend com base no paciente escolhido:
  - plano de saúde individual/familiar ativo;
  - dependentes do plano familiar;
  - empresa/convênio empresarial vinculado ao paciente;
  - se o plano ou empresa estiver inativo, vencido ou suspenso, o desconto não é aplicado.
- Convênios foram tratados como **empresas conveniadas**, com percentual de desconto próprio.
- Planos de saúde foram separados em **Individual** e **Familiar**, com dependentes e percentual de desconto do plano.
- Mensagens rápidas agora têm tela própria no estilo solicitado, com prefixo, emojis iniciais/finais, categoria, favorito, copiar e apagar.
- Mensagens rápidas continuam isoladas por usuário no backend: cada médico/usuário vê somente os próprios cards, exceto administradores conforme escopo do sistema.
- Produtos continuam com imagem, categoria, preço, estoque, status e opção de permitir ou não desconto.

Como testar:

1. Entrar como `admin / admin123456`.
2. Acessar `/produtos/` e cadastrar produtos com imagem.
3. Acessar `/convenios/` e cadastrar uma empresa com desconto.
4. Acessar `/pacientes/`, editar um paciente e vincular a empresa.
5. Acessar `/planos-saude/`, criar plano Individual ou Familiar ativo e definir desconto.
6. Acessar `/financeiro/`, escolher o paciente e vender produtos.
7. Conferir se o desconto aparece automaticamente e se o recibo fica disponível para download.
8. Acessar `/mensagens-rapidas/` como médico e criar cards; depois entrar com outro usuário para confirmar isolamento.

## Atualização - Exames e assinatura médica

### Melhorias aplicadas
- Criado cadastro de assinatura médica digitalizada no menu do perfil.
- Criado campo de registro profissional para CRM/COREN/CRP ou equivalente.
- Criada biblioteca de modelos de exames médicos realistas, organizada por categoria.
- Exame agora pode ser criado a partir de modelo pronto, editado pelo médico e assinado digitalmente.
- Documento imprimível do exame disponível em formato visual de laudo médico, com opção de imprimir/salvar em PDF pelo navegador.
- Paciente continua restrito aos próprios exames finalizados/entregues.
- Médicos e laboratório continuam protegidos por RBAC no backend.

### Como testar
1. Entrar como `medico / medico123456`.
2. Abrir o menu do perfil e acessar `Minha assinatura médica`.
3. Enviar uma imagem de assinatura e informar o registro profissional.
4. Ir em `Exames` > `Biblioteca de modelos`.
5. Escolher um modelo, editar o texto e marcar `Assinar este exame agora`.
6. Salvar e abrir `Documento` para visualizar o laudo com assinatura.

### Pontos de atenção para produção
- Usar armazenamento privado ou bucket com regras de acesso para assinaturas médicas.
- Registrar hash/versão da assinatura no momento da emissão se for necessário valor legal forte.
- Definir processo interno para validação de CRM/registro profissional.
