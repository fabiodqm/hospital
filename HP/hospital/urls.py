from django.urls import path

from . import views

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pacientes/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('arquivados/', views.archive_list, name='archive_list'),
    path('relatorios/', views.reports, name='reports'),
    path('administracao/', views.admin_panel, name='admin_panel'),
    path('administracao/usuarios/novo/', views.user_create, name='user_create'),
    path('administracao/usuarios/<int:pk>/editar/', views.user_edit, name='user_edit'),
    path('portal-paciente/', views.patient_portal, name='patient_portal'),
    path('financeiro/<int:pk>/recibo/', views.sale_receipt_download, name='sale_receipt_download'),
    path('perfil/', views.profile_account, name='profile_account'),
    path('perfil/assinatura/', views.profile_signature, name='profile_signature'),
    path('exames/modelos/biblioteca/', views.exam_template_library, name='exam_template_library'),
    path('exames/<int:pk>/documento/', views.exam_print, name='exam_print'),
    path('auth/discord/', views.discord_login_start, name='discord_login_start'),
    path('<slug:slug>/', views.module_list, name='module_list'),
    path('<slug:slug>/novo/', views.module_create, name='module_create'),
    path('<slug:slug>/<int:pk>/editar/', views.module_edit, name='module_edit'),
    path('<slug:slug>/<int:pk>/arquivar/', views.module_archive, name='module_archive'),
    path('<slug:slug>/<int:pk>/excluir/', views.module_delete, name='module_delete'),
]
