from django import forms

from .models import Bot

class BotForm(forms.ModelForm):
    key = forms.CharField(label='Key', widget=forms.TextInput())
    secret = forms.CharField(label='Secret', widget=forms.TextInput())
    confidence = forms.CharField(label='Confidence', widget=forms.TextInput())
    risk = forms.CharField(label='Risk', widget=forms.TextInput())
    reward = forms.CharField(label='Reward', widget=forms.TextInput())
    test = forms.CharField(widget= forms.CheckboxInput())
    
    class Meta:
        model = Bot
        fields = [
            "key",
            "secret",
            "test",
            "confidence",
            "risk",
            "reward",
            ]