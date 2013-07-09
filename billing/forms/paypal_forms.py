from django import forms
import re

from paypal.standard.forms import (PayPalPaymentsForm,
                                   PayPalEncryptedPaymentsForm)


INTEGER_FIELDS = ('amount_', 'item_number_', 'quantity_', 'tax_', 'shipping_',
                  'shipping2_', 'discount_amount_', 'discount_amount2_',
                  'discount_rate_', 'discount_rate2_', 'discount_num_',
                  'tax_rate_')
INTEGER_FIELD_RE = re.compile(r'|'.join(re.escape(f) for f in INTEGER_FIELDS))

CHAR_FIELDS = ('item_name_', 'on0_', 'on1_', 'os0_', 'os1_')
CHAR_FIELD_RE = re.compile(r'|'.join(re.escape(f) for f in CHAR_FIELDS))


class MultipleItemsMixin(object):
    """
    Use the initial data as a heuristic to create a form
    that accepts multiple items
    """

    def __init__(self, **kwargs):
        super(MultipleItemsMixin, self).__init__(**kwargs)
        has_multiple_items = False
        if 'initial' in kwargs:
            for k, v in kwargs['initial'].items():
                if INTEGER_FIELD_RE.match(k):
                    self.fields[k] = forms.IntegerField(
                        widget=forms.widgets.HiddenInput())
                    has_multiple_items = True
                elif CHAR_FIELD_RE.match(k):
                    has_multiple_items = True
                    self.fields[k] = forms.CharField(
                        widget=forms.widgets.HiddenInput())
        if has_multiple_items:
            self.fields['upload'] = forms.IntegerField(
                initial=1,
                widget=forms.widgets.HiddenInput())
            del self.fields['amount']
            del self.fields['item_name']
            self.initial['cmd'] = '_cart'


class MerchantPayPalPaymentsForm(MultipleItemsMixin, PayPalPaymentsForm):
    pass


class MerchantPayPalEncryptedPaymentsForm(MultipleItemsMixin, PayPalEncryptedPaymentsForm):
    pass
