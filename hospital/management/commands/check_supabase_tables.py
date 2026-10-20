from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Verifica se as tabelas principais existem no banco conectado.'

    def handle(self, *args, **options):
        existing_tables = set(connection.introspection.table_names())
        missing = []
        for model in apps.get_app_config('hospital').get_models():
            table = model._meta.db_table
            if table not in existing_tables:
                missing.append(table)
        if not missing:
            self.stdout.write(self.style.SUCCESS('Todas as tabelas do app hospital existem.'))
            return
        self.stdout.write(self.style.WARNING('Tabelas ausentes:'))
        for table in missing:
            self.stdout.write(f'- {table}')
        self.stdout.write('Execute: python manage.py makemigrations && python manage.py migrate')
