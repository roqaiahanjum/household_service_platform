from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WorkerProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'area', 'is_staff')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    list_filter = UserAdmin.list_filter + ('role', 'area')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number', 'address', 'area', 'profile_picture')}),
    )

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_status', 'is_available', 'average_rating')
    list_filter = ('verification_status', 'is_available', 'service_areas')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'skills')
    filter_horizontal = ('service_areas',)
    actions = ['approve_providers']

    @admin.action(description='Approve selected providers')
    def approve_providers(self, request, queryset):
        updated = queryset.update(verification_status=WorkerProfile.VerificationStatus.VERIFIED)
        self.message_user(request, f'Successfully approved {updated} provider(s).')
