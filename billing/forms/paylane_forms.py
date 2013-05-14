# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from billing.utils.credit_card import InvalidCard, Visa, MasterCard
from billing.utils.countries import COUNTRIES

curr_year = datetime.datetime.now().year
month_choices = ((ii, ii) for ii in range(1, 13))
year_choices = ((ii, ii) for ii in range(curr_year, curr_year + 7))


class PaylaneForm(forms.Form):
    name_on_card = forms.CharField(label=_("Name on card"), max_length=50)
    street_house = forms.CharField(label=_("Address"), max_length=46)
    city = forms.CharField(label=_("City"), max_length=40)
    state_address = forms.CharField(label=_("State"), max_length=40, required=False)
    zip_code = forms.CharField(label=_("Zip Code"), max_length=9)
    country_code = forms.ChoiceField(COUNTRIES, label=_("Country"))
    card_number = forms.RegexField(label=_("Card Number"), max_length=19, regex=r'[0-9]{13,19}$')
    card_code = forms.RegexField(label=_("Card Code"), max_length=4, regex=r'[0-9]{3,4}$')
    issue_number = forms.RegexField(label=_("Issue Number"), max_length=3, required=False, regex=r'[0-9]{1,3}$')
    expiration_month = forms.ChoiceField(label=_("Expiration date"), choices=month_choices)
    expiration_year = forms.ChoiceField(label=_("Expiration year"), choices=year_choices)

    def clean(self):
        cleaned_data = super(PaylaneForm, self).clean()

        if not self._errors:
            name = cleaned_data.get('name_on_card', '').split(' ', 1)
            first_name = name[0]
            last_name = ' '.join(name[1:])

            cc = Visa(first_name=first_name,
                    last_name=last_name,
                    month=cleaned_data.get('expiration_month'),
                    year=cleaned_data.get('expiration_year'),
                    number=cleaned_data.get('card_number'),
                    verification_value=cleaned_data.get('card_code'))

            if cc.is_expired():
                raise forms.ValidationError(_('This credit card has expired.'))

            if not cc.is_luhn_valid():
                raise forms.ValidationError(_('This credit card number isn\'t valid'))

            if not cc.is_valid():
                #this should never occur
                raise forms.ValidationError(_('Invalid credit card'))

            options = {
                    'customer': cleaned_data.get('name_on_card'),
                    'email': '',
                    'order_id': '',
                    'ip': '',
                    'description': '',
                    'merchant': '',
                    'billing_address': {
                            'name': cleaned_data.get('name_on_card'),
                            'company': '',
                            'address1': cleaned_data.get('street_house'),
                            'address2': '',
                            'city': cleaned_data.get('city'),
                            'state': '',
                            'country': cleaned_data.get('country_code'),
                            'zip': cleaned_data.get('zip_code'),
                            'phone': '',
                        },
                    'shipping_address': {}
                }

            cleaned_data['paylane'] = {
                    'credit_card': cc,
                    'options': options
                }

        return cleaned_data
