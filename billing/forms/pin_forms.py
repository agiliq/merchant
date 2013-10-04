import re
from datetime import date
from django import forms
from billing import CreditCard
from billing.models.pin_models import PinCard

class CardNumberField(forms.CharField):
    """
    Field for entering card number, validates using mod 10
    """
    def clean(self, value):
        value = super(CardNumberField, self).clean(value)
        value = value.replace('-', '').replace(' ', '')
        if not verify_mod10(value):
            raise forms.ValidationError('The card number is not valid.')
        return value

def verify_mod10(ccnum):
    """
    Check a credit card number for validity using the mod10 algorithm.
    """
    ccnum = re.sub(r'[^0-9]', '', ccnum)
    double, sum = 0, 0
    for i in range(len(ccnum) - 1, -1, -1):
            for c in str((double + 1) * int(ccnum[i])): sum = sum + int(c)
            double = (double + 1) % 2
    return ((sum % 10) == 0)

class PinChargeForm(forms.ModelForm):
    number = CardNumberField()
    expiry_month = forms.IntegerField(min_value=1,
                            max_value=12,
                            widget=forms.NumberInput(attrs={'placeholder':'MM'}))
    expiry_year = forms.IntegerField(min_value=date.today().year,
                            max_value=date.today().year+20,
                            widget=forms.NumberInput(attrs={'placeholder':'YYYY'}))
    cvc = forms.IntegerField(min_value=0, max_value=9999)
    email = forms.EmailField()
    description = forms.CharField(max_length=255)

    user_fields = ('email', 'first_name', 'last_name')

    class Meta:
        model = PinCard
        exclude = []

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PinChargeForm, self).__init__(*args, **kwargs)
        # If we're supplying a valid user already, we can either leave the
        # fields in the template, pre-populated; or leave them out completely
        if user:
            for field in self.user_fields:
                self.fields[field].required = False
                value = getattr(user, field, None)
                if value:
                    self.fields[field].initial = value

    def get_credit_card(self):
        d = self.cleaned_data
        d['month'] = d['expiry_month']
        d['year'] = d['expiry_year']
        d['verification_value'] = d['cvc']
        card = CreditCard(**d)
        options = {
            'email': d['email'],
            'description': d['description'],
            'billing_address': {
                'address1': d['address_line1'],
                'address2': d.get('address_line2'),
                'city': d['address_city'],
                'zip': d['address_postcode'],
                'state': d['address_state'],
                'country': d['address_country'],
            }
        }
        return card, options
