# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Booking, BookingStatusLog

import csv
from django.http import HttpResponse

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'service', 'worker', 'status', 'scheduled_datetime', 'total_price')
    list_filter = ('status', 'scheduled_datetime')
    search_fields = ('customer__username', 'customer__first_name', 'worker__username', 'service__name')
    list_editable = ('status', 'worker')
    date_hierarchy = 'scheduled_datetime'
    actions = ['mark_as_completed', 'mark_as_cancelled', 'export_to_csv']

    @admin.action(description='Mark selected bookings as Completed')
    def mark_as_completed(self, request, queryset):
        queryset.update(status=Booking.Status.COMPLETED)
        self.message_user(request, 'Selected bookings marked as completed.')

    @admin.action(description='Mark selected bookings as Cancelled')
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status=Booking.Status.CANCELLED)
        self.message_user(request, 'Selected bookings marked as cancelled.')

    @admin.action(description='Export selected bookings to CSV')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookings_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Customer', 'Service', 'Worker', 'Status', 'Date', 'Price'])
        
        for booking in queryset:
            writer.writerow([
                booking.id, 
                booking.customer.get_full_name() or booking.customer.username, 
                booking.service.name, 
                booking.worker.get_full_name() if booking.worker else 'Unassigned', 
                booking.status, 
                booking.scheduled_datetime.strftime("%Y-%m-%d %H:%M"), 
                booking.total_price
            ])
            
        return response

@admin.register(BookingStatusLog)
class BookingStatusLogAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'timestamp')

from .models import WorkPhoto

@admin.register(WorkPhoto)
class WorkPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'provider', 'is_approved', 'uploaded_at')
    list_filter = ('is_approved', 'uploaded_at')
    search_fields = ('provider__username', 'booking__id', 'caption')
    actions = ['approve_photos', 'reject_photos']
    
    @admin.action(description='Approve selected photos')
    def approve_photos(self, request, queryset):
        queryset.update(is_approved=True, rejection_reason='')
        
        # Also update the booking
        for photo in queryset:
            photo.booking.photos_approved = True
            photo.booking.save()
            
        self.message_user(request, 'Selected photos approved successfully.')

    @admin.action(description='Reject selected photos')
    def reject_photos(self, request, queryset):
        queryset.update(is_approved=False, rejection_reason='Rejected by admin.')
        
        for photo in queryset:
            photo.booking.photos_approved = False
            photo.booking.save()
            
        self.message_user(request, 'Selected photos rejected.')
