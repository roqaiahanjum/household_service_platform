from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import CreateView, TemplateView
from .forms import CustomerSignUpForm, WorkerSignUpForm, UserUpdateForm, WorkerProfileUpdateForm
from .models import User, WorkerProfile
from bookings.models import Booking, WorkPhoto
from django.contrib.auth.mixins import LoginRequiredMixin

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
        if self.request.user.role == User.Role.WORKER:
            return ['accounts/worker_dashboard.html']
        return ['accounts/customer_dashboard.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == User.Role.WORKER:
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
