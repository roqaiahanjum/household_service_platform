from django.contrib import admin
from .models import Area, Review

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'service_name', 'rating', 'created_at')
    list_filter = ('rating', 'city')
