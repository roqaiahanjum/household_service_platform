from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Service
from core.models import Review

class CategoryListView(ListView):
    model = Category
    template_name = 'services/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Area
        
        selected_area_id = self.request.GET.get('area')
        if not selected_area_id and self.request.user.is_authenticated and hasattr(self.request.user, 'area') and self.request.user.area:
            selected_area_id = self.request.user.area.id
            
        context['areas'] = Area.objects.filter(is_active=True)
        if selected_area_id:
            try:
                context['selected_area'] = Area.objects.get(id=selected_area_id)
            except Area.DoesNotExist:
                pass
        return context

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch reviews for this service (case-insensitive contains match to be safe)
        context['reviews'] = Review.objects.filter(service_name__icontains=self.object.name)
        # Fetch related services from the same category
        context['related_services'] = Service.objects.filter(
            category=self.object.category, 
            is_active=True
        ).exclude(id=self.object.id)[:3]
        
        # Fetch approved work photos for this service
        from bookings.models import WorkPhoto
        context['work_photos'] = WorkPhoto.objects.filter(booking__service=self.object, is_approved=True).order_by('-uploaded_at')[:4]
        
        return context
