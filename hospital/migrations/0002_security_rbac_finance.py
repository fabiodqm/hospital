# Generated manually for Centro Médico SHINE improvements.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InsuranceProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=140, unique=True)),
                ('default_discount_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('contact', models.CharField(blank=True, max_length=160)),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Convênio',
                'verbose_name_plural': 'Convênios',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=140)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('category', models.CharField(choices=[('Consulta', 'Consulta'), ('Procedimento', 'Procedimento'), ('Medicamento', 'Medicamento'), ('Material', 'Material'), ('Serviço', 'Serviço'), ('Outros', 'Outros')], default='Serviço', max_length=40)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('discount_allowed', models.BooleanField(default=True)),
                ('applicable_provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='hospital.insuranceprovider')),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RoleChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('previous_role', models.CharField(blank=True, max_length=80)),
                ('new_role', models.CharField(max_length=80)),
                ('reason', models.TextField(blank=True)),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='role_changes_made', to=settings.AUTH_USER_MODEL)),
                ('changed_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='role_changes_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Log de alteração de cargo',
                'verbose_name_plural': 'Logs de alteração de cargos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='discord_id',
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='discord_username',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='discord_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='healthinsuranceplan',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plans', to='hospital.insuranceprovider', verbose_name='Convênio'),
        ),
        migrations.AddField(
            model_name='sale',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='hospital.insuranceprovider', verbose_name='Convênio aplicado'),
        ),
        migrations.AddField(
            model_name='sale',
            name='original_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='sale',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='sale',
            name='discount_applied_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_discount_applied', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='saleitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_items', to='hospital.product'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='hospital_pr_name_aa6b21_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['category'], name='hospital_pr_categor_b6e5c1_idx'),
        ),
    ]
