from django import forms
from .models import LivestockItem, LivestockImage

# 1. Form for Creating Livestock (Step 1)
class LivestockItemForm(forms.ModelForm):
    class Meta:
        model = LivestockItem
        fields = ['species', 'breed', 'tag_id', 'age', 'weight', 'gender', 'price', 'description', 'is_for_sale']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super(LivestockItemForm, self).__init__(*args, **kwargs)
        # Add Bootstrap styling to all fields
        for field in self.fields:
            if field != 'is_for_sale':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})

# 2. Form for Uploading Images (Step 2)
class LivestockImageForm(forms.ModelForm):
    class Meta:
        model = LivestockImage
        fields = ['image']
        
    def __init__(self, *args, **kwargs):
        super(LivestockImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

# 3. Form for Placing Orders (THIS WAS MISSING)
class SimpleOrderForm(forms.Form):
    inquiry_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'placeholder': 'Optional: Ask the farmer about delivery, price, or health records.',
            'class': 'form-control'
        }),
        required=False
    )
    # Hidden field for quantity (defaults to 1)
    quantity = forms.IntegerField(initial=1, min_value=1, widget=forms.HiddenInput())