from django import forms

from .models import Strategy

class StrategyForm(forms.ModelForm):
    
    confidence = forms.DecimalField(initial=0.80, label='Confidence', widget=forms.TextInput())
    risk = forms.DecimalField(initial=0.01, label='Risk', widget=forms.TextInput())
    reward = forms.DecimalField(initial=0.02, label='Reward', widget=forms.TextInput())
    
    class Meta:
        model = Strategy
        fields = [
            "confidence",
            "risk",
            "reward",
            ]