# Deploy do Centro Médico SHINE — Render + Supabase

## Arquitetura

- Django executado no Render com Gunicorn.
- Supabase PostgreSQL como banco relacional (`DATABASE_URL`).
- Supabase Storage via API S3 para fotos de perfil, assinaturas, imagens de produtos, anexos de exames e comprovantes.
- WhiteNoise para arquivos estáticos versionados.
- Turso não é usado: é um banco de dados, não um serviço de armazenamento de arquivos. Não misture a conexão Turso com `DATABASE_URL` do Django.

## 1. Preparar o Supabase

### PostgreSQL

No projeto Supabase, abra **Project Settings → Database → Connect** e copie uma connection string PostgreSQL compatível com conexões de servidor. Configure-a em `DATABASE_URL` no Render. Use uma conexão com SSL; se o endereço direto não funcionar na rede/plano escolhido, use o pooler de sessão recomendado pelo Supabase para aplicações persistentes. Não use a connection string do navegador nem a chave `anon` como conexão PostgreSQL.

### Storage

1. Abra **Storage** e crie um bucket privado, por exemplo `shine-private-media`.
2. Em **Storage → S3 Connection**, habilite/consulte as credenciais S3 e copie o endpoint, a região, o Access Key ID e o Secret Access Key gerados para S3.
3. Não use a `service_role` key como chave S3. Não torne o bucket público: ele pode conter assinaturas médicas e documentos pessoais.
4. Mantenha cópia segura das credenciais. As chaves S3 têm privilégios amplos no Storage; use-as apenas no servidor Render.

## 2. Publicar no GitHub

Envie os arquivos do projeto, incluindo `render.yaml`, `build.sh` e `requirements.txt`. Não envie `.env`, `db.sqlite3`, `media/`, exportações de dados ou credenciais. O `.gitignore` deste pacote bloqueia esses itens.

## 3. Criar o serviço Render

1. No Render, escolha **New → Blueprint** e conecte o repositório com `render.yaml`, ou crie um Web Service manualmente.
2. Runtime: Python.
3. Build command: `bash build.sh`.
4. Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`.
5. Configure no painel todas as variáveis `sync: false` solicitadas pelo Blueprint:
   - `DATABASE_URL`
   - `SUPABASE_S3_ENDPOINT_URL` (normalmente formato `https://<project-ref>.storage.supabase.co/storage/v1/s3`)
   - `SUPABASE_S3_REGION` (copiada da página S3 do projeto)
   - `SUPABASE_S3_BUCKET` (ex.: `shine-private-media`)
   - `SUPABASE_S3_ACCESS_KEY_ID`
   - `SUPABASE_S3_SECRET_ACCESS_KEY`
6. `SECRET_KEY` é gerada pelo Blueprint. `DEBUG=False` e `MEDIA_STORAGE=supabase` já estão definidos.
7. Se usar domínio próprio, acrescente o domínio em `ALLOWED_HOSTS` e `https://seu-dominio` em `CSRF_TRUSTED_ORIGINS`.

O endpoint e a região devem ser copiados da configuração S3 do Supabase, sem adivinhar valores. O backend assina URLs temporárias para arquivos privados; não compartilhe links assinados e lembre que eles expiram.

## 4. Banco existente (SQLite) — não perder dados

O banco local `db.sqlite3` não é enviado ao Render. Se ele contém registros que precisam continuar existindo, faça a migração de dados antes de colocar o site em uso:

1. Faça uma cópia de segurança local do `db.sqlite3` e da pasta `media/`.
2. Em ambiente local, confirme que `DATABASE_URL` está vazio para usar SQLite e exporte os dados de aplicação para um arquivo local protegido:

   `DATABASE_URL= python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --indent 2 > shine-data-export.json`

   No PowerShell, use `$env:DATABASE_URL=''; python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --indent 2 > shine-data-export.json`.

3. Configure `DATABASE_URL` para o Supabase no ambiente controlado e execute primeiro `python manage.py migrate`; em seguida execute `python manage.py loaddata shine-data-export.json`. Faça primeiro em um projeto de teste, pois conflitos de chaves/constraints podem exigir uma migração específica.
4. Não coloque `shine-data-export.json` no GitHub: ele pode conter dados pessoais e de saúde. Apague o arquivo após validar a importação e guarde o backup apenas em local seguro.

Se o banco SQLite não contém dados que precisam ser mantidos, basta executar as migrations no deploy e criar uma conta administrativa com `python manage.py createsuperuser` no Shell do Render. Não execute `seed_base_data` em produção sem revisar o comando e trocar as senhas de demonstração.

## 5. Migrar arquivos de mídia existentes

Antes de publicar, faça backup da pasta `media/`. Configure localmente as variáveis `MEDIA_STORAGE=supabase`, `SUPABASE_S3_ENDPOINT_URL`, `SUPABASE_S3_REGION`, `SUPABASE_S3_BUCKET`, `SUPABASE_S3_ACCESS_KEY_ID` e `SUPABASE_S3_SECRET_ACCESS_KEY`. Execute:

`python manage.py migrate_local_media`

O comando copia os arquivos da pasta local para o bucket, mantendo caminhos como `profiles/`, `signatures/`, `exams/`, `products/` e `payments/`. Por padrão, não sobrescreve objetos que já existem. Verifique no painel do Supabase se os arquivos foram enviados antes de remover qualquer cópia local.

## 6. Validação após deploy

- Confira os logs de build e confirme que `collectstatic` e `migrate` terminaram sem erro.
- Abra `/login/`, faça login e confira dashboard e permissões.
- Teste upload e leitura de foto de perfil, assinatura médica e imagem de produto.
- Teste anexos de exames e comprovantes, caso esses módulos estejam em uso.
- Confira os URLs de mídia: devem ser URLs assinadas e temporárias, não links públicos permanentes.
- Verifique que `DEBUG=False`, HTTPS e cookies seguros estão ativos.
- Faça backup do PostgreSQL e defina uma rotina de backup dos arquivos do bucket.

## Limites importantes

- O deploy não migra automaticamente os dados de SQLite nem os arquivos de mídia: siga as etapas 4 e 5 se precisar preservar os dados atuais.
- A execução de migrations ocorre no build command por simplicidade e segue o guia de Django do Render; para fluxos com requisitos rigorosos de zero downtime, use o comando de pre-deploy conforme o plano do Render e teste as migrations em staging.
- Como este é um sistema médico, valide controles de acesso, privacidade/LGPD, retenção e backups antes de inserir dados reais.
