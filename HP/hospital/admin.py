from django.contrib import admin

from .models import (
    Admission,
    Appointment,
    ArchivedRecord,
    AuditLog,
    Bed,
    BloodDonationScreening,
    Exam,
    ExamTemplate,
    HealthInsurancePlan,
    InsuranceProvider,
    MedicalDocument,
    MedicalRecord,
    Patient,
    PlasterRecord,
    PregnancyFollowUp,
    Product,
    QuickMessage,
    Role,
    RoleChangeLog,
    Sale,
    SaleItem,
    Specialty,
    StudentSupervision,
    SystemSetting,
    UserProfile,
    UserSpecialty,
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'document', 'phone', 'email', 'company_provider', 'status')
    search_fields = ('full_name', 'document', 'phone', 'email')
    list_filter = ('status', 'gender', 'blood_type', 'company_provider')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'can_manage_system', 'is_active_profile')
    list_filter = ('role', 'can_manage_system', 'is_active_profile')
    search_fields = ('user__username', 'display_name', 'phone')


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')


@admin.register(UserSpecialty)
class UserSpecialtyAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'is_primary', 'can_attend', 'can_sign_documents', 'can_access_records')
    list_filter = ('specialty', 'can_attend', 'can_sign_documents', 'can_access_records')


@admin.register(StudentSupervision)
class StudentSupervisionAdmin(admin.ModelAdmin):
    list_display = ('student_user', 'supervisor_user', 'specialty', 'is_active')
    list_filter = ('is_active', 'specialty')


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'operator', 'provider', 'original_total', 'discount_percent', 'discount_amount', 'discount_source', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [SaleItemInline]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'module', 'object_label', 'ip_address')
    list_filter = ('action', 'module', 'created_at')
    search_fields = ('object_label', 'message', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Role)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(Bed)
admin.site.register(Admission)

@admin.register(ExamTemplate)
class ExamTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'exam_type', 'sample_material', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'exam_type', 'template_content', 'conclusion_template')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam_type', 'patient', 'requesting_doctor', 'issue_date', 'status', 'signed_by', 'signed_at')
    list_filter = ('status', 'issue_date', 'template')
    search_fields = ('exam_type', 'patient__full_name', 'report', 'conclusion')
admin.site.register(MedicalDocument)
admin.site.register(BloodDonationScreening)
admin.site.register(PregnancyFollowUp)
admin.site.register(PlasterRecord)
admin.site.register(HealthInsurancePlan)
admin.site.register(QuickMessage)
admin.site.register(SystemSetting)
admin.site.register(ArchivedRecord)


@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_discount_percent', 'is_active')
    search_fields = ('name', 'contact')
    list_filter = ('is_active',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'discount_allowed')
    search_fields = ('name', 'description')
    list_filter = ('category', 'is_active', 'discount_allowed')


@admin.register(RoleChangeLog)
class RoleChangeLogAdmin(admin.ModelAdmin):
    list_display = ('changed_user', 'previous_role', 'new_role', 'changed_by', 'created_at')
    search_fields = ('changed_user__username', 'changed_by__username', 'reason')
    list_filter = ('new_role', 'created_at')
    readonly_fields = ('changed_by', 'changed_user', 'previous_role', 'new_role', 'reason', 'created_at', 'updated_at')
