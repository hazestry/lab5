from django.contrib import admin
from .models import TourRoute

@admin.register(TourRoute)
class TourRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'length_km', 'difficulty', 'members_count', 'created_at', 'updated_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['name', 'description', 'difficulty']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Характеристики маршрута', {
            'fields': ('length_km', 'difficulty', 'members_count')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
