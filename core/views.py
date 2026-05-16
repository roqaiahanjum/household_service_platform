from django.shortcuts import render
from django.views.generic import TemplateView
from services.models import Category, Service
from core.models import Review, Area
from accounts.models import WorkerProfile

class HomeView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Area Selection Logic
        selected_area_id = self.request.GET.get('area')
        if not selected_area_id and self.request.user.is_authenticated and hasattr(self.request.user, 'area') and self.request.user.area:
            selected_area_id = self.request.user.area.id
            
        context['areas'] = Area.objects.filter(is_active=True)
        
        if selected_area_id:
            try:
                selected_area = Area.objects.get(id=selected_area_id, is_active=True)
                context['selected_area'] = selected_area
                context['expert_count'] = WorkerProfile.objects.filter(service_areas=selected_area, is_available=True, verification_status='VERIFIED').count()
            except Area.DoesNotExist:
                context['selected_area'] = None
                context['expert_count'] = 0
                
        context['categories'] = Category.objects.filter(services__is_active=True).distinct()[:8]
        context['services'] = Service.objects.filter(is_active=True)
        context['reviews'] = Review.objects.all()
        
        from bookings.models import WorkPhoto
        context['latest_photos'] = WorkPhoto.objects.filter(is_approved=True).order_by('-uploaded_at')[:6]
        
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

class GalleryView(TemplateView):
    template_name = 'core/gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from bookings.models import WorkPhoto
        
        photos = WorkPhoto.objects.filter(is_approved=True).order_by('-uploaded_at')
        
        service_id = self.request.GET.get('service')
        if service_id:
            photos = photos.filter(booking__service_id=service_id)
            
        area_id = self.request.GET.get('area')
        if area_id:
            photos = photos.filter(booking__customer__area_id=area_id)
            
        context['photos'] = photos
        context['services'] = Service.objects.filter(is_active=True)
        context['areas'] = Area.objects.filter(is_active=True)
        return context
