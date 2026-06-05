# Central Pet - Produção, Deploy e Backup

## Variáveis de ambiente

Configure estas variáveis no Railway:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=uma-chave-forte
DEBUG=False
ALLOWED_HOSTS=seudominio.com.br,www.seudominio.com.br,central-pet.up.railway.app
CSRF_TRUSTED_ORIGINS=https://seudominio.com.br,https://www.seudominio.com.br,https://central-pet.up.railway.app
SENTRY_DSN=https://...
ENVIRONMENT=production
RELEASE=central-pet-1.0.0
SECURE_SSL_REDIRECT=True
USE_X_FORWARDED_HOST=True
TRUST_PROXY_SSL_HEADER=True
SECURE_HSTS_PRELOAD=True
BOOTSTRAP_ADMIN=true
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@seudominio.com.br
ADMIN_PASSWORD=uma-senha-forte
```

Localmente, deixe `DATABASE_URL` vazio para usar SQLite.

## Railway e PostgreSQL

1. Crie o projeto no Railway.
2. Adicione um serviço PostgreSQL.
3. Conecte a variável `DATABASE_URL` do PostgreSQL ao serviço Django.
4. Configure as demais variáveis acima.
5. O `Procfile` inicia a aplicação com:

```bash
gunicorn central_pet.wsgi:application --bind 0.0.0.0:$PORT
```

6. Configure no Railway um comando de pre-deploy/deploy para preparar banco, estáticos e administrador sem depender de terminal:

```bash
python manage.py migrate && python manage.py collectstatic --noinput && python manage.py bootstrap_admin
```

## Sentry

1. Crie um projeto Django no Sentry.
2. Copie o DSN para `SENTRY_DSN`.
3. Defina `ENVIRONMENT=production`.
4. Em desenvolvimento, acesse `/__debug__/sentry/` para testar.
5. Em produção, essa rota retorna 404.

## Backup PostgreSQL

Backup manual:

```bash
pg_dump "$DATABASE_URL" > backup-central-pet.sql
```

Backup compactado:

```bash
pg_dump "$DATABASE_URL" | gzip > backup-central-pet.sql.gz
```

## Restore

Restaure em um banco vazio ou recém-criado:

```bash
psql "$DATABASE_URL" < backup-central-pet.sql
```

Para arquivo compactado:

```bash
gzip -dc backup-central-pet.sql.gz | psql "$DATABASE_URL"
```

## Operação segura

- Nunca deixe `DEBUG=True` em produção.
- Nunca versione `.env` real.
- Use somente `jpg`, `jpeg`, `png` e `webp` em uploads.
- Restrinja `/painel/` a usuários `staff` ou `superuser`.
- Faça backup antes de grandes alterações no painel.
- Use `SECURE_HSTS_PRELOAD=True` apenas depois de confirmar que o domínio e subdomínios servem HTTPS corretamente na Cloudflare.

## Arquivos de mídia

Hoje os uploads funcionam localmente em `MEDIA_ROOT=media/` e são servidos em desenvolvimento com `DEBUG=True`.

Em produção, o disco do Railway não deve ser considerado armazenamento permanente para banners, produtos e serviços. Antes de uso intensivo em produção, migre mídia para armazenamento externo, preferencialmente Cloudflare R2.

Preparação recomendada para a futura migração:

1. Criar bucket privado/público no Cloudflare R2.
2. Configurar domínio ou subdomínio para mídia, por exemplo `media.seudominio.com.br`.
3. Adicionar uma dependência de storage compatível com S3 quando a migração for feita.
4. Configurar `DEFAULT_FILE_STORAGE`/`STORAGES` e credenciais por variável de ambiente.
5. Migrar arquivos existentes de `media/` para o bucket.
6. Validar banners, produtos e serviços no painel antes de remover mídia local.

Não guarde credenciais R2 no código.
