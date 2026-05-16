from django.urls import path
from .views import BookingCreateView, BookingDetailView, BookingListView, BookingStatusUpdateView, WorkPhotoCreateView, BookingSuccessView

app_name = 'bookings'

urlpatterns = [
    path('create/<slug:slug>/', BookingCreateView.as_view(), name='booking_create'),
    path('<int:pk>/success/', BookingSuccessView.as_view(), name='booking_success'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('<int:pk>/update-status/', BookingStatusUpdateView.as_view(), name='status_update'),
    path('<int:pk>/upload-photos/', WorkPhotoCreateView.as_view(), name='upload_photos'),
    path('my-bookings/', BookingListView.as_view(), name='booking_list'),
]
