from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Copia os arquivos existentes em MEDIA_ROOT para o storage configurado, preservando os caminhos.'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true', help='Substitui arquivos que já existem no destino.')

    def handle(self, *args, **options):
        source_root = Path(settings.MEDIA_ROOT)
        if not source_root.exists():
            raise CommandError(f'A pasta de mídia local não existe: {source_root}')
        if settings.MEDIA_STORAGE != 'supabase':
            raise CommandError('Configure MEDIA_STORAGE=supabase e as credenciais S3 antes de executar este comando.')

        files = [path for path in source_root.rglob('*') if path.is_file()]
        if not files:
            self.stdout.write(self.style.WARNING('Nenhum arquivo local encontrado em MEDIA_ROOT.'))
            return

        copied = 0
        skipped = 0
        for path in files:
            relative_name = path.relative_to(source_root).as_posix()
            if default_storage.exists(relative_name) and not options['overwrite']:
                skipped += 1
                self.stdout.write(f'Ignorado (já existe): {relative_name}')
                continue
            if default_storage.exists(relative_name) and options['overwrite']:
                default_storage.delete(relative_name)
            with path.open('rb') as source:
                saved_name = default_storage.save(relative_name, File(source, name=relative_name))
            copied += 1
            self.stdout.write(f'Enviado: {saved_name}')

        self.stdout.write(self.style.SUCCESS(f'Concluído. Enviados: {copied}; ignorados: {skipped}.'))
