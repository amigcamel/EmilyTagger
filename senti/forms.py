from django import forms

class SentiTagForm(forms.Form):
    cue = forms.CharField(widget=forms.HiddenInput())
    tag = forms.IntegerField(widget=forms.HiddenInput())
