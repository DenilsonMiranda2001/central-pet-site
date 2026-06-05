from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria o administrador inicial a partir de variáveis de ambiente, sem sobrescrever usuários existentes."

    def handle(self, *args, **options):
        enabled = config("BOOTSTRAP_ADMIN", default=False, cast=bool)
        if not enabled:
            self.stdout.write("BOOTSTRAP_ADMIN não está ativo. Nenhuma ação executada.")
            return

        username = config("ADMIN_USERNAME", default="").strip()
        email = config("ADMIN_EMAIL", default="").strip()
        password = config("ADMIN_PASSWORD", default="")

        missing = [
            name for name, value in {
                "ADMIN_USERNAME": username,
                "ADMIN_EMAIL": email,
                "ADMIN_PASSWORD": password,
            }.items() if not value
        ]
        if missing:
            raise CommandError(f"Variáveis obrigatórias ausentes: {', '.join(missing)}")

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Usuário "{username}" já existe. Senha e permissões não foram alteradas.'
            ))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Administrador "{username}" criado com sucesso.'))
