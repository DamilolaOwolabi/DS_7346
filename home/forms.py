# forms.py
from django import forms

class GroceryPreferenceForm(forms.Form):
    price_range = forms.ChoiceField(
        choices=[('$', 'Low'), ('$$', 'Medium'), ('$$$', 'High')],
        label="Price Range"
    )
    quality = forms.ChoiceField(
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        label="Quality"
    )
    brand_preference = forms.CharField(max_length=50, required=False, label="Brand Preference")
    max_calories = forms.IntegerField(required=False, label="Max Caloric Value")
    distance = forms.IntegerField(label="Max Distance to Store (in miles)")

    def __init__(self, *args, **kwargs):
        super(GroceryPreferenceForm, self).__init__(*args, **kwargs)
        # Apply the 'form-control' class to each field widget
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
