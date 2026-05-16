from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, WorkerProfile
from core.models import Area
from django.core.exceptions import ValidationError

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'area', 'profile_picture']

class WorkerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ['skills', 'experience_years', 'bio', 'base_rate_per_hour', 'is_available', 'service_areas', 'identity_proof']

    def clean_service_areas(self):
        service_areas = self.cleaned_data.get('service_areas')
        if service_areas and service_areas.count() > 2:
            raise ValidationError('You can only select a maximum of 2 service areas.')
        return service_areas

class CustomerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'area')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        if commit:
            user.save()
        return user

class WorkerSignUpForm(UserCreationForm):
    skills = forms.CharField(widget=forms.Textarea)
    experience_years = forms.IntegerField(min_value=0)
    service_areas = forms.ModelMultipleChoiceField(
        queryset=Area.objects.filter(is_active=True),
        widget=forms.SelectMultiple,
        required=True
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address')

    def clean_service_areas(self):
        service_areas = self.cleaned_data.get('service_areas')
        if service_areas and service_areas.count() > 2:
            raise ValidationError('You can only select a maximum of 2 service areas.')
        return service_areas

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.WORKER
        if commit:
            user.save()
            from .models import WorkerProfile
            profile = WorkerProfile.objects.create(
                user=user,
                skills=self.cleaned_data.get('skills'),
                experience_years=self.cleaned_data.get('experience_years')
            )
            profile.service_areas.set(self.cleaned_data.get('service_areas'))
        return user
