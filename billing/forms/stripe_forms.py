from django import forms

class StripeForm(forms.Form):
    credit_card_number = forms.CharField(max_length=16)
    credit_card_cvc = forms.CharField(max_length=4)
    credit_card_expiration_month = forms.CharField(max_length=2)
    credit_card_expiration_year = forms.CharField(max_length=2)
