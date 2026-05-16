from django import template
from accounts.models import User, WorkerProfile
from bookings.models import Booking
from django.utils import timezone
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def get_admin_dashboard_stats():
    today = timezone.now().date()
    
    # Total Users
    total_users = User.objects.count()
    
    # Bookings Today
    today_bookings = Booking.objects.filter(scheduled_datetime__date=today).count()
    
    # Total Revenue (All completed bookings)
    total_revenue = Booking.objects.filter(status='COMPLETED').aggregate(total=Sum('total_price'))['total'] or 0
    
    # Pending Approvals (Workers)
    pending_workers = WorkerProfile.objects.filter(verification_status='PENDING').count()
    
    # Recent Bookings (Last 5)
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    
    # New Provider Requests
    new_providers = WorkerProfile.objects.filter(verification_status='PENDING').select_related('user').order_by('-user__date_joined')[:5]
    
    return {
        'total_users': total_users,
        'today_bookings': today_bookings,
        'total_revenue': total_revenue,
        'pending_workers': pending_workers,
        'recent_bookings': recent_bookings,
        'new_providers': new_providers,
    }
