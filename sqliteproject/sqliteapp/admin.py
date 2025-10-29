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
    
    # Дополнительные настройки для удобства
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    # Действия
    actions = ['mark_as_easy', 'mark_as_hard']
    
    def mark_as_easy(self, request, queryset):
        updated = queryset.update(difficulty='Легкий')
        self.message_user(request, f'Обновлено {updated} маршрутов на "Легкий"')
    mark_as_easy.short_description = 'Отметить как "Легкий"'
    
    def mark_as_hard(self, request, queryset):
        updated = queryset.update(difficulty='Тяжелый')
        self.message_user(request, f'Обновлено {updated} маршрутов на "Тяжелый"')
    mark_as_hard.short_description = 'Отметить как "Тяжелый"'