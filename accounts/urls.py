from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomerSignUpView, WorkerSignUpView, DashboardView, ProfileView

app_name = 'accounts'

urlpatterns = [
    path('signup/customer/', CustomerSignUpView.as_view(), name='customer_signup'),
    path('signup/worker/', WorkerSignUpView.as_view(), name='worker_signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
