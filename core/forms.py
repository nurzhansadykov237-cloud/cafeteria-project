from django import forms
from .models import Dish


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = [
            "category",
            "name",
            "description",
            "price",
            "is_available",
        ]
        widgets = {
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "name": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01"
            }),
            "is_available": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }