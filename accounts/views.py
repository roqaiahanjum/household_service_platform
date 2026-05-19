from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView, TemplateView
from .forms import CustomerSignUpForm, WorkerSignUpForm, UserUpdateForm, WorkerProfileUpdateForm
from .models import User, WorkerProfile
from bookings.models import Booking, WorkPhoto
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy

class CustomLoginView(DjangoLoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and (user.role == User.Role.ADMIN or user.is_superuser):
            return reverse_lazy('accounts:dashboard')
        return super().get_success_url()

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if not request.user.is_admin():
                raise PermissionDenied
        return self.get_response(request)



class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'accounts/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('accounts:dashboard')

class WorkerSignUpView(CreateView):
    model = User
    form_class = WorkerSignUpForm
    template_name = 'accounts/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'worker'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('accounts:dashboard')

from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

class DashboardView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        user = self.request.user
        if user.role == User.Role.ADMIN or user.is_superuser:
            return ['accounts/dashboard.html']
        if user.role == User.Role.WORKER:
            return ['accounts/worker_dashboard.html']
        return ['accounts/customer_dashboard.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == User.Role.ADMIN or user.is_superuser:
            from core.models import Area, Review
            from services.models import Service
            
            context['total_users'] = User.objects.count()
            context['total_workers'] = User.objects.filter(role=User.Role.WORKER).count()
            context['total_customers'] = User.objects.filter(role=User.Role.CUSTOMER).count()
            context['total_bookings'] = Booking.objects.count()
            context['total_areas'] = Area.objects.count()
            context['total_revenue'] = Booking.objects.filter(status='COMPLETED').aggregate(total=Sum('total_price'))['total'] or 0
            
            context['workers'] = WorkerProfile.objects.all().select_related('user', 'user__area')
            context['customers'] = User.objects.filter(role=User.Role.CUSTOMER).select_related('area').prefetch_related('bookings')
            context['bookings'] = Booking.objects.all().select_related('customer', 'service', 'service__category', 'worker')
            context['all_workers'] = User.objects.filter(role=User.Role.WORKER)
            context['services'] = Service.objects.all().select_related('category')
            context['reviews'] = Review.objects.all()
            
        elif user.role == User.Role.WORKER:
            today = timezone.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            start_of_month = today.replace(day=1)
            
            context['todays_bookings'] = user.assigned_jobs.filter(
                scheduled_datetime__date=today
            ).order_by('scheduled_datetime')
            
            context['today_earnings'] = Booking.objects.filter(
                worker=user, 
                status='COMPLETED',
                scheduled_datetime__date=today
            ).aggregate(total=Sum('total_price'))['total'] or 0

            context['week_earnings'] = Booking.objects.filter(
                worker=user, 
                status='COMPLETED',
                scheduled_datetime__date__range=[today - timedelta(days=today.weekday()), today]
            ).aggregate(total=Sum('total_price'))['total'] or 0

            context['month_earnings'] = Booking.objects.filter(
                worker=user, 
                status='COMPLETED',
                scheduled_datetime__year=today.year,
                scheduled_datetime__month=today.month
            ).aggregate(total=Sum('total_price'))['total'] or 0
            
            context['portfolio_photos'] = WorkPhoto.objects.filter(provider=user).order_by('-uploaded_at')
            context['approved_photos_count'] = context['portfolio_photos'].filter(is_approved=True).count()
            
        else:
            all_bookings = user.bookings.all().order_by('-scheduled_datetime')
            
            context['active_bookings'] = all_bookings.exclude(status__in=['COMPLETED', 'CANCELLED'])
            context['past_bookings'] = all_bookings.filter(status__in=['COMPLETED', 'CANCELLED'])
            
            context['total_spent'] = user.bookings.filter(
                status='COMPLETED'
            ).aggregate(total=Sum('total_price'))['total'] or 0
            
            # Simple way to get unique addresses from past bookings
            addresses = user.bookings.values_list('address', flat=True).distinct()
            context['saved_addresses'] = [addr for addr in addresses if addr][:3]
            
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        if self.request.user.role == User.Role.WORKER:
            if 'worker_form' not in context:
                worker_profile, created = WorkerProfile.objects.get_or_create(user=self.request.user)
                context['worker_form'] = WorkerProfileUpdateForm(instance=worker_profile)
        return context

    def post(self, request, *args, **kwargs):
        from django.contrib import messages
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        worker_form = None
        
        if request.user.role == User.Role.WORKER:
            worker_profile, created = WorkerProfile.objects.get_or_create(user=request.user)
            worker_form = WorkerProfileUpdateForm(request.POST, request.FILES, instance=worker_profile)
            
            if user_form.is_valid() and worker_form.is_valid():
                user_form.save()
                worker_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('accounts:profile')
        else:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('accounts:profile')
                
        context = self.get_context_data(user_form=user_form, worker_form=worker_form)
        return self.render_to_response(context)


from django.views.generic import DetailView

class WorkerProfileDetailView(DetailView):
    """
    View to display a worker's professional profile along with their average ratings
    and all reviews they have received from customers.
    """
    model = WorkerProfile
    template_name = 'accounts/worker_profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the worker's user account
        worker = self.object.user
        # Pull all reviews written for this worker, prefetching the customer's details for efficiency
        context['reviews'] = worker.reviews_received.select_related('customer').order_by('-created_at')
        return context

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required(login_url='accounts:login')
@require_POST
def update_worker_status(request, worker_id):
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        if new_status not in ['PENDING', 'VERIFIED', 'REJECTED']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        worker = WorkerProfile.objects.get(id=worker_id)
        worker.verification_status = new_status
        worker.save()
        return JsonResponse({'success': True, 'status': worker.verification_status})
    except WorkerProfile.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required(login_url='accounts:login')
@require_POST
def assign_worker_view(request, booking_id):
    if not request.user.is_admin():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        if not worker_id:
            return JsonResponse({'error': 'Worker ID is required'}, status=400)
        
        booking = Booking.objects.get(id=booking_id)
        worker = User.objects.get(id=worker_id, role=User.Role.WORKER)
        
        booking.worker = worker
        if booking.status in ['PENDING', 'CONFIRMED']:
            booking.status = 'ASSIGNED'
        booking.save()
        
        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'worker_id': worker.id,
            'worker_name': worker.get_full_name() or worker.username
        })
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Worker not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



