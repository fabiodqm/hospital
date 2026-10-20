# Generated for Centro Médico SHINE - modelos de exames e assinatura médica

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hospital.models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0004_rename_hospital_pr_name_aa6b21_idx_hospital_pr_name_7470af_idx_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=180, unique=True)),
                ('category', models.CharField(choices=[('Laboratorial', 'Laboratorial'), ('Imagem', 'Imagem'), ('Cardiologia', 'Cardiologia'), ('Neurologia', 'Neurologia'), ('Pneumologia', 'Pneumologia'), ('Ginecologia/Obstetrícia', 'Ginecologia/Obstetrícia'), ('Endoscopia', 'Endoscopia'), ('Patologia', 'Patologia'), ('Oftalmologia/Otorrino', 'Oftalmologia/Otorrino'), ('Outros', 'Outros')], default='Laboratorial', max_length=60)),
                ('exam_type', models.CharField(max_length=180)),
                ('body_system', models.CharField(blank=True, max_length=120)),
                ('sample_material', models.CharField(blank=True, max_length=140)),
                ('clinical_indication', models.TextField(blank=True)),
                ('preparation', models.TextField(blank=True)),
                ('template_content', models.TextField(help_text='Modelo editável do laudo/solicitação médica.')),
                ('conclusion_template', models.TextField(blank=True)),
                ('recommendations', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Modelo de exame',
                'verbose_name_plural': 'Modelos de exames',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='signature_image',
            field=models.ImageField(blank=True, null=True, upload_to='signatures/', validators=[hospital.models.validate_safe_image]),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='signature_registered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='professional_license',
            field=models.CharField(blank=True, help_text='CRM, COREN, CRP ou registro profissional.', max_length=80),
        ),
        migrations.AddField(
            model_name='exam',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exams', to='hospital.examtemplate'),
        ),
        migrations.AddField(
            model_name='exam',
            name='clinical_indication',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='sample_material',
            field=models.CharField(blank=True, max_length=140),
        ),
        migrations.AddField(
            model_name='exam',
            name='findings',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='conclusion',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='recommendations',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='signed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='signed_exams', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exam',
            name='signed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='examtemplate',
            index=models.Index(fields=['category', 'is_active'], name='hospital_ex_category_80e9_idx'),
        ),
        migrations.AddIndex(
            model_name='examtemplate',
            index=models.Index(fields=['exam_type'], name='hospital_ex_exam_ty_7ff8_idx'),
        ),
    ]
