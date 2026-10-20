# Centro Médico SHINE - Sistema Hospitalar Django

Sistema web hospitalar em Django, com landing page, painel administrativo, área médica, financeiro, RBAC, auditoria e integração Supabase/PostgreSQL opcional.

## Contas de teste

O comando `seed_base_data` cria:

- Admin: `admin` / `admin123456`
- Médico: `medico` / `medico123456`

## Start rápido no Windows

Extraia o ZIP e dê duplo clique em:

```txt
START.bat
```

Ele cria/usa a venv, instala dependências, roda migrations, cria dados base e abre o site.

## URLs

- Landing: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login/`
- Painel: `http://127.0.0.1:8000/dashboard/`
- Admin Django: `http://127.0.0.1:8000/admin/`

## Instalação manual

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_base_data
python manage.py runserver
```

## Principais melhorias desta versão

- Sidebar no estilo enviado, com ícones coloridos, item ativo com recorte e hover suave.
- Dropdown premium do usuário com foto, perfil, atalhos e modo claro/escuro.
- Landing com imagem real e seção Sobre Nós.
- RBAC com Admin, Direção, Chefias, Médicos, Residentes, Enfermagem, Financeiro e Recepção.
- Mensagens rápidas individuais por médico/usuário.
- Produtos com imagem, preço, categoria, estoque e status.
- Convênios com desconto padrão.
- Vendas com convênio, valor original, desconto e total.
- Logs de alteração de cargo.
- Rate limit simples no login.
- Headers de segurança.
- Preparação para Discord OAuth.

## Supabase

Configure no `.env`:

```txt
DATABASE_URL=postgresql://...
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ANON_KEY=
```

Depois rode:

```bash
python manage.py migrate
python manage.py seed_base_data
```

## Auditoria

Leia `AUDITORIA_FINAL.md` para ver fragilidades encontradas, correções, testes de permissão e recomendações de produção.

### Atualização desta versão

- Financeiro refeito em formato de caixa com produtos cadastrados prontos para venda.
- Recibo gerado para download, sem upload de comprovante.
- Convênio agora representa empresa conveniada com desconto automático.
- Plano de saúde agora é Individual ou Familiar, com dependentes e desconto próprio.
- Mensagens rápidas refeitas no estilo solicitado e individuais por médico/usuário.

Rotas principais:

- `/financeiro/` — Caixa e vendas.
- `/produtos/` — Cadastro de produtos com imagem.
- `/convenios/` — Empresas conveniadas e desconto.
- `/planos-saude/` — Plano individual/familiar com dependentes.
- `/mensagens-rapidas/` — Cards rápidos individuais.

## Exames médicos e assinatura

A área de exames possui biblioteca de modelos prontos, laudo editável e documento para impressão/PDF. Médicos autorizados podem cadastrar assinatura em `Minha assinatura médica`, disponível no dropdown do perfil.

Fluxo sugerido:
1. Entrar como médico.
2. Cadastrar assinatura médica.
3. Abrir `Exames`.
4. Usar um modelo da biblioteca.
5. Editar o laudo.
6. Marcar assinatura e salvar.
7. Abrir o documento do exame.
