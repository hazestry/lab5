from django.db import models

class TourRoute(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название маршрута")
    description = models.TextField(verbose_name="Описание")
    length_km = models.FloatField(verbose_name="Длина (км)")
    difficulty = models.CharField(max_length=50, verbose_name="Сложность")
    members_count = models.IntegerField(verbose_name="Количество участников")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Туристический маршрут"
        verbose_name_plural = "Туристические маршруты"
        ordering = ['-created_at']
        unique_together = ['name', 'length_km', 'difficulty']

    def __str__(self):
        return f"{self.name} ({self.length_km} км)"