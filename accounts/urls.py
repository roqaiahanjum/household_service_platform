from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomerSignUpView, WorkerSignUpView, DashboardView, ProfileView, WorkerProfileDetailView, update_worker_status, CustomLoginView

app_name = 'accounts'

urlpatterns = [
    path('signup/customer/', CustomerSignUpView.as_view(), name='customer_signup'),
    path('signup/worker/', WorkerSignUpView.as_view(), name='worker_signup'),
    path('login/', CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('worker/<int:pk>/', WorkerProfileDetailView.as_view(), name='worker_profile'),
    path('admin/workers/<int:worker_id>/update/', update_worker_status, name='update_worker_status'),
]

