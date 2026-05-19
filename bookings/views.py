# pyrefly: ignore [missing-import]

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
from django.db.models import Count, Q

def auto_assign_worker(customer, service):
    """
    Auto assign logic:
    1. Get customer's area from their profile
    2. Find all VERIFIED workers in that area
    3. Filter only available workers (is_available = True)
    4. Pick the worker with highest rating first
    5. If rating is same, pick least busy worker (fewest active bookings)
    6. Assign that worker to the booking
    """
    from accounts.models import WorkerProfile
    
    if not hasattr(customer, 'area') or not customer.area:
        return None

    # Active statuses for counting busy workers
    active_statuses = ['PENDING', 'CONFIRMED', 'ASSIGNED', 'ON_THE_WAY', 'IN_PROGRESS']
    
    # Find all eligible verified workers in the customer's area who are available
    eligible_profiles = WorkerProfile.objects.filter(
        service_areas=customer.area,
        is_available=True,
        verification_status__iexact='verified',
        skills__icontains=service.name
    ).annotate(
        active_bookings_count=Count('user__assigned_jobs', filter=Q(user__assigned_jobs__status__in=active_statuses))
    ).order_by('-average_rating', 'active_bookings_count')
    
    if eligible_profiles.exists():
        return eligible_profiles.first().user
    return None

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
            
        date = form.cleaned_data['date']
        time_str = form.cleaned_data['time_slot']
        duration = int(form.cleaned_data['duration'])
        phone = form.cleaned_data['phone_number']
        
        from datetime import datetime
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        start_datetime = datetime.combine(date, time_obj)
        
        # 6. Assign that worker to the booking
        assigned_worker = auto_assign_worker(customer, service)
        
        form.instance.scheduled_datetime = start_datetime
        form.instance.instructions = f"Duration: {duration} Hour(s) | Phone: {phone}"
        form.instance.customer = customer
        form.instance.service = service
        form.instance.total_price = service.price_per_unit * duration
        
        if assigned_worker:
            form.instance.worker = assigned_worker
            # 7. Change booking status from PENDING to CONFIRMED automatically
            form.instance.status = 'CONFIRMED'
            messages.success(self.request, "Your booking is confirmed! Worker will contact you soon")
        else:
            form.instance.worker = None
            # 8. If no worker available in that area, keep status as PENDING and show message
            form.instance.status = 'PENDING'
            messages.info(self.request, "We will assign a worker soon")
            
        response = super().form_valid(form)
        
        log_notes = f"System automatically assigned {assigned_worker.get_full_name() or assigned_worker.username}" if assigned_worker else "Waiting for manual assignment."
        BookingStatusLog.objects.create(
            booking=self.object,
            status=self.object.status,
            notes=log_notes
        )
        
        return response

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


from .models import WorkerReview
from .forms import WorkerReviewForm
from django.db.models import Avg

class WorkerReviewCreateView(LoginRequiredMixin, CreateView):
    """
    View for customers to rate and review a completed booking.
    Enforces restrictions:
    1. Only the customer of the booking can review.
    2. Only completed bookings can be reviewed.
    3. Exactly one review per booking is permitted.
    """
    model = WorkerReview
    form_class = WorkerReviewForm
    template_name = 'bookings/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Fetch the booking matching the URL path parameter
        booking = get_object_or_404(Booking, pk=self.kwargs['booking_id'])
        
        # Rule 1: Enforce customer ownership check
        if booking.customer != request.user:
            messages.error(request, "You are not authorized to review this booking.")
            return redirect('accounts:dashboard')
            
        # Rule 2: Ensure booking is fully completed before allowing feedback
        if booking.status != 'COMPLETED':
            messages.error(request, "You can only review completed bookings.")
            return redirect('accounts:dashboard')
            
        # Rule 3: Enforce one review per booking check
        if hasattr(booking, 'worker_review'):
            messages.error(request, "You have already reviewed this booking.")
            return redirect('accounts:dashboard')
            
        # Rule 4: Ensure there is an assigned worker to review
        if not booking.worker:
            messages.error(request, "Cannot review a booking with no assigned worker.")
            return redirect('accounts:dashboard')
            
        # Keep reference to the validated booking object
        self.booking = booking
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Inject booking details into context for rendering in the star rating form
        context = super().get_context_data(**kwargs)
        context['booking'] = self.booking
        return context

    def form_valid(self, form):
        # Automatically bind key relationships on save
        form.instance.booking = self.booking
        form.instance.customer = self.request.user
        form.instance.worker = self.booking.worker
        
        response = super().form_valid(form)
        
        # Recalculate average rating of the worker and update WorkerProfile
        worker = self.booking.worker
        if hasattr(worker, 'worker_profile'):
            profile = worker.worker_profile
            # Aggregate rating score from all reviews submitted for this worker
            avg_rating = WorkerReview.objects.filter(worker=worker).aggregate(avg=Avg('rating'))['avg']
            if avg_rating is not None:
                profile.average_rating = round(avg_rating, 2)
                profile.save()
                
        messages.success(self.request, "Thank you! Your rating and review have been submitted successfully.")
        return response

    def get_success_url(self):
        # Redirect customer back to their dashboard upon successful review
        return reverse('accounts:dashboard')