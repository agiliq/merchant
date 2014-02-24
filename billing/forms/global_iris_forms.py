import datetime

from django import forms

from billing.forms.common import CreditCardFormBase

class CreditCardForm(CreditCardFormBase):

    cardholders_name = forms.CharField(label="Card holder's name", required=True)
    number = forms.CharField(required=True)
    month = forms.ChoiceField(label="Expiry month", choices=[])
    year = forms.ChoiceField(label="Expiry year", choices=[])
    verification_value = forms.CharField(label='CVV', required=True)

    def __init__(self, *args, **kwargs):
        super(CreditCardForm, self).__init__(*args, **kwargs)
        self.fields['year'].choices = self.get_year_choices()
        self.fields['month'].choices = self.get_month_choices()

    def get_year_choices(self):
        today = datetime.date.today()
        return [(y, y) for y in range(today.year, today.year + 21)]

    def get_month_choices(self):
        # Override if you want month names, for instance.
        return [(m, m) for m in range(1, 13)]

