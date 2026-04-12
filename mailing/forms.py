from django import forms


class EmailSubscribeForm(forms.Form):
    email = forms.EmailField(label="Your email address")
