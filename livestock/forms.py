# livestock/forms.py
from django import forms
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
            'tag_id': forms.TextInput(attrs={'placeholder': 'e.g., KGL001', 'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age in months', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Weight in kg', 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'placeholder': 'RWF 150,000', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'species': forms.Select(attrs={'class': 'form-select'}),
            'breed': forms.Select(attrs={'class': 'form-select'}),
        }
        
# --- 2. IMAGE UPLOAD FORM (Step 2: Add Photos) ---
class LivestockImageForm(forms.ModelForm):
    class Meta:
        model = LivestockImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

# --- 3. ORDER FORM (For Payments) ---
class SimpleOrderForm(forms.Form):
    # Field for buyer to send a message
    inquiry_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional: Ask about delivery or health records...'}),
        required=False
    )
    # Hidden field for quantity (defaults to 1)
    quantity = forms.IntegerField(initial=1, min_value=1, widget=forms.HiddenInput())
    


class CheckoutContactForm(forms.ModelForm):  # <--- Changed 'models' to 'forms'
    class Meta:
        model = Order
        fields = ['contact_phone', 'delivery_address']
        widgets = {
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 078 000 0000'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'District, Sector, Cell, specific landmark...'}),
        }