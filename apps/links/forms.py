from django import forms


class LinkForm(forms.Form):
    url = forms.URLField(max_length=255)
