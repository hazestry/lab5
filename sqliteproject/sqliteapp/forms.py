from django import forms
from .models import TourRoute

SAVE_LOCATION_CHOICES = [
    ('db', 'база данных'),
    ('file', 'XML-файл'),
]

class TourRouteForm(forms.ModelForm):
    save_location = forms.ChoiceField(
        choices=SAVE_LOCATION_CHOICES,
        widget=forms.RadioSelect,
        label="куда сохранить?",
        initial='db'
    )

    class Meta:
        model = TourRoute
        fields = ['name', 'description', 'length_km', 'difficulty', 'members_count']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'введите название маршрута'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'описание маршрута'}),
            'length_km': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'длина в километрах'}),
            'difficulty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'например: легкий, средний, тяжелый'}),
            'members_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'количество участников'}),
        }
        labels = {
            'name': 'название маршрута',
            'description': 'описание',
            'length_km': 'длина (км)',
            'difficulty': 'сложность',
            'members_count': 'количество участников',
        }

    def clean_length_km(self):
        length = self.cleaned_data.get('length_km')
        if length <= 0:
            raise forms.ValidationError("длина маршрута должна быть больше 0.")
        return length

    def clean_members_count(self):
        count = self.cleaned_data.get('members_count')
        if count < 0:
            raise forms.ValidationError("количество участников не может быть отрицательным.")
        return count


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск маршрутов...',
            'id': 'search-input'
        })
    )