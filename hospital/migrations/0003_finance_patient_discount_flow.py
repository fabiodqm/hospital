import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0002_security_rbac_finance'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='company_provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_patients', to='hospital.insuranceprovider', verbose_name='Empresa / convênio empresarial'),
        ),
        migrations.AddField(
            model_name='healthinsuranceplan',
            name='discount_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Desconto do plano (%)'),
        ),
        migrations.AddField(
            model_name='sale',
            name='discount_source',
            field=models.CharField(blank=True, max_length=255, verbose_name='Origem do desconto'),
        ),
        migrations.AlterField(
            model_name='healthinsuranceplan',
            name='plan_type',
            field=models.CharField(choices=[('Individual', 'Individual'), ('Familiar', 'Familiar')], default='Individual', max_length=80),
        ),
        migrations.AlterField(
            model_name='healthinsuranceplan',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plans', to='hospital.insuranceprovider', verbose_name='Empresa vinculada (opcional)'),
        ),
    ]
