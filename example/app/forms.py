
import datetime

from django import forms

from billing.credit_card import CreditCard

class CreditCardForm(forms.Form):
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
    
    first_name = forms.CharField()
    last_name = forms.CharField()
    month = forms.ChoiceField(choices=MONTH_CHOICES)
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    number = forms.CharField()
    card_type = forms.ChoiceField(choices=CARD_TYPES, required=False)
    verification_value = forms.CharField(label='CVV')

    def clean(self):
        data = self.cleaned_data
        credit_card = CreditCard(**data)
        if not credit_card.is_valid():
            raise forms.ValidationError('Credit card validation failed')
        return data

   