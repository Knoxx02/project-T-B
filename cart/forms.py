from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'postal_code']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }