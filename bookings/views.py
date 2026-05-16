# pyrefly: ignore [missing-import]

from django.shortcuts import render, redirect, get_object_or_404
# pyrefly: ignore [missing-import]
from django.views.generic import CreateView, ListView, DetailView, UpdateView
# pyrefly: ignore [missing-import]
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Booking, BookingStatusLog
from .forms import BookingForm
from services.models import Service
from django.urls import reverse_lazy, reverse
from django.contrib import messages

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_slug = self.kwargs.get('slug')
        context['service'] = get_object_or_404(Service, slug=service_slug)
        return context

    def get_success_url(self):
        return reverse('bookings:booking_success', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        service_slug = self.kwargs.get('slug')
        service = get_object_or_404(Service, slug=service_slug)
        
        customer = self.request.user
        if not hasattr(customer, 'area') or not customer.area:
            messages.error(self.request, "Please update your profile with your Area before booking.")
            return redirect('accounts:profile')
            
        from accounts.models import WorkerProfile
        providers_in_area = WorkerProfile.objects.filter(
            service_areas=customer.area,
            is_available=True,
            verification_status='VERIFIED'
        )
        
        if not providers_in_area.exists():
            messages.error(self.request, f"Sorry, we currently have no verified providers available in {customer.area.name}.")
            return redirect('services:category_list')

        date = form.cleaned_data['date']
        time_str = form.cleaned_data['time_slot']
        duration = int(form.cleaned_data['duration'])
        phone = form.cleaned_data['phone_number']
        
        from datetime import datetime
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        form.instance.scheduled_datetime = datetime.combine(date, time_obj)
        
        form.instance.instructions = f"Duration: {duration} Hour(s) | Phone: {phone}"
        form.instance.customer = customer
        form.instance.service = service
        form.instance.total_price = service.price_per_unit * duration
        
        return super().form_valid(form)

class BookingSuccessView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_success.html'
    context_object_name = 'booking'



class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        if self.request.user.role == 'WORKER':
            return Booking.objects.filter(worker=self.request.user)
        return Booking.objects.filter(customer=self.request.user)

class BookingStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = ['status']
    
    def form_valid(self, form):
        booking = form.save()
        BookingStatusLog.objects.create(
            booking=booking,
            status=booking.status,
            notes=f"Status updated by {self.request.user.get_full_name()}"
        )
        messages.success(self.request, f"Status updated to {booking.get_status_display()}")
        return redirect('bookings:booking_detail', pk=booking.pk)

from django.views.generic.edit import CreateView
from django.urls import reverse
from .models import WorkPhoto
from .forms import WorkPhotoForm

class WorkPhotoCreateView(LoginRequiredMixin, CreateView):
    model = WorkPhoto
    form_class = WorkPhotoForm
    template_name = 'bookings/work_photo_form.html'
    
    def form_valid(self, form):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'], worker=self.request.user)
        if booking.status != 'COMPLETED':
            messages.error(self.request, "You can only upload photos for completed jobs.")
            return redirect('accounts:dashboard')
        
        if hasattr(booking, 'photos') and booking.photos.exists():
            messages.error(self.request, "Photos already uploaded for this job.")
            return redirect('accounts:dashboard')

        form.instance.booking = booking
        form.instance.provider = self.request.user
        response = super().form_valid(form)
        
        booking.has_photos = True
        booking.save()
        
        messages.success(self.request, "Work photos uploaded successfully and are pending admin approval.")
        return response
        
    def get_success_url(self):
        return reverse('accounts:dashboard')
