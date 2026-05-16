from django.db import models
from django.conf import settings
from services.models import Service
from django.utils.translation import gettext_lazy as _

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        ASSIGNED = 'ASSIGNED', _('Assigned')
        ON_THE_WAY = 'ON_THE_WAY', _('On the Way')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        limit_choices_to={'role': 'CUSTOMER'}
    )
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='bookings')
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_jobs',
        limit_choices_to={'role': 'WORKER'}
    )
    
    scheduled_datetime = models.DateTimeField()
    address = models.TextField()
    instructions = models.TextField(blank=True, null=True)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='PENDING') # PENDING, PAID, REFUNDED
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Photos tracking
    has_photos = models.BooleanField(default=False)
    photos_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.service.name} for {self.customer.get_full_name()}"

class BookingStatusLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20, choices=Booking.Status.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.booking.id} changed to {self.status} at {self.timestamp}"

class WorkPhoto(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='photos')
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_photos')
    before_photo = models.ImageField(upload_to='work_photos/before/')
    after_photo = models.ImageField(upload_to='work_photos/after/')
    caption = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Work Photos for Booking #{self.booking.id}"
