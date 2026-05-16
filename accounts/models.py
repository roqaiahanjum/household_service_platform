from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        CUSTOMER = 'CUSTOMER', _('Customer')
        WORKER = 'WORKER', _('Worker')

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    area = models.ForeignKey('core.Area', on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_worker(self):
        return self.role == self.Role.WORKER

class WorkerProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        VERIFIED = 'VERIFIED', _('Verified')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    skills = models.TextField(help_text="Enter skills separated by commas")
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True, null=True)
    base_rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    identity_proof = models.FileField(upload_to='verification/', blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    service_areas = models.ManyToManyField('core.Area', blank=True, related_name='providers')

    def __str__(self):
        return f"Worker Profile: {self.user.get_full_name() or self.user.username}"
