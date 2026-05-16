# pyrefly: ignore [missing-import]
from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg', 'id': 'booking-date'}),
        label="Select Date"
    )
    
    TIME_CHOICES = [
        ('09:00', 'Morning (9 AM - 12 PM)'),
        ('13:00', 'Afternoon (1 PM - 4 PM)'),
        ('17:00', 'Evening (5 PM - 8 PM)'),
    ]
    time_slot = forms.ChoiceField(
        choices=TIME_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
        label="Select Time"
    )
    
    DURATION_CHOICES = [
        (1, '1 Hour'),
        (2, '2 Hours'),
        (3, '3 Hours'),
    ]
    duration = forms.ChoiceField(
        choices=DURATION_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
        label="Select Duration"
    )
    
    phone_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. +91 9876543210'}),
        label="Phone Number"
    )

    class Meta:
        model = Booking
        fields = ['address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control form-control-lg', 'placeholder': 'Enter your full address'}),
        }

from .models import WorkPhoto
from django.core.exceptions import ValidationError
import os

class WorkPhotoForm(forms.ModelForm):
    class Meta:
        model = WorkPhoto
        fields = ['before_photo', 'after_photo', 'caption']
        widgets = {
            'caption': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'e.g. Deep cleaned bathroom in Tilakwadi'}),
        }

    def clean_photo(self, photo_field_name):
        photo = self.cleaned_data.get(photo_field_name)
        if photo:
            # Check file size (5MB limit)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError(f"Image file too large ( > 5MB ).")
            # Check extension
            ext = os.path.splitext(photo.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError(f"Unsupported file extension. Allowed extensions: {', '.join(valid_extensions)}")
        return photo

    def clean_before_photo(self):
        return self.clean_photo('before_photo')

    def clean_after_photo(self):
        return self.clean_photo('after_photo')
