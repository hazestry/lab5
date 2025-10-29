from django import forms
from .models import TourRoute

SAVE_LOCATION_CHOICES = [
    ('db', 'База данных'),
    ('file', 'XML файл'),
]

class TourRouteForm(forms.ModelForm):
    save_location = forms.ChoiceField(
        choices=SAVE_LOCATION_CHOICES,
        widget=forms.RadioSelect,
        label="Куда сохранить",
        initial='db'
    )

    class Meta:
        model = TourRoute
        fields = ['name', 'description', 'length_km', 'difficulty', 'members_count']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название маршрута'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание маршрута'}),
            'length_km': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Длина в километрах'}),
            'difficulty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Легкий, Средний, Тяжелый'}),
            'members_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество участников'}),
        }
        labels = {
            'name': 'Название маршрута',
            'description': 'Описание',
            'length_km': 'Длина (км)',
            'difficulty': 'Сложность',
            'members_count': 'Количество участников',
        }

    def clean_length_km(self):
        length = self.cleaned_data.get('length_km')
        if length <= 0:
            raise forms.ValidationError("Длина маршрута должна быть больше 0.")
        return length

    def clean_members_count(self):
        count = self.cleaned_data.get('members_count')
        if count < 0:
            raise forms.ValidationError("Количество участников не может быть отрицательным.")
        return count


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию, описанию или сложности...',
            'id': 'search-input'
        })
    )