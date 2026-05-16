from django.urls import path
from .views import CategoryListView, ServiceDetailView

app_name = 'services'

urlpatterns = [
    path('', CategoryListView.as_view(), name='category_list'),
    path('<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
]
