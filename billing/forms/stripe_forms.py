from django import forms
from django.conf import settings
import stripe


class StripeForm(forms.Form):
    credit_card__number = forms.CharField()
    credit_card__cvc = forms.CharField(max_length=4)
    credit_card__expiration_month = forms.CharField(max_length=7)
    credit_card__expiration_year = forms.CharField(max_length=7)
