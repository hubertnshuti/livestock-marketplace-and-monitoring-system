# livestock/forms.py
from django import forms
# FIX: Ensure all livestock models are imported from the local models file
from .models import LivestockItem, LivestockImage, LivestockSpecies, Breed, OrderItem, Order 


# --- 1. CORE LISTING FORM (Step 1: Basic Info) ---
class LivestockItemForm(forms.ModelForm):
    species = forms.ModelChoiceField(queryset=LivestockSpecies.objects.all(), required=True)
    breed = forms.ModelChoiceField(queryset=Breed.objects.all(), required=False)
    
    class Meta:
        model = LivestockItem
        fields = [
            'species', 
            'breed', 
            'tag_id', 
            'age', 
            'weight', 
            'gender', 
            'price', 
            'description',
            'is_for_sale'
        ]
        widgets = {
            'tag_id': forms.TextInput(attrs={'placeholder': 'e.g., KGL001'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age in months'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Weight in kg'}),
            'price': forms.NumberInput(attrs={'placeholder': 'RWF 150,000'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
# --- 2. IMAGE UPLOAD FORM (Step 2: Add Photos) ---
class LivestockImageForm(forms.ModelForm):
    class Meta:
        model = LivestockImage
        fields = ['image']

# --- 3. SIMPLE ORDER FORM (Used on Detail Page) ---
class SimpleOrderForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'})
    )