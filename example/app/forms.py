
import datetime

from django import forms

from billing import CreditCard

CARD_TYPES = [
    ('', ''),
    ('visa', 'Visa'),
    ('master', 'Master'),
    ('discover', 'Discover'),
    ('american_express', 'American Express'),
    ('diners_club', 'Diners Club'),
    # ('jcb', ''),
    # ('switch', ''),
    # ('solo', ''),
    # ('dankort', ''),
    ('maestro', 'Maestro'),
    # ('forbrugsforeningen', ''),
    # ('laser', 'Laser'),
    ]

today = datetime.date.today()
MONTH_CHOICES = [(m, datetime.date(today.year, m, 1).strftime('%b')) for m in range(1, 13)]
YEAR_CHOICES = [(y, y) for y in range(today.year, today.year + 21)]


class CreditCardForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    month = forms.ChoiceField(choices=MONTH_CHOICES)
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    number = forms.CharField(required=False)
    card_type = forms.ChoiceField(choices=CARD_TYPES, required=False)
    verification_value = forms.CharField(label='CVV', required=False)

    def clean(self):
        data = self.cleaned_data
        credit_card = CreditCard(**data)
        if not credit_card.is_valid():
            raise forms.ValidationError('Credit card validation failed')
        return data
