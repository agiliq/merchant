from django import forms


from paypal.standard.forms import (PayPalPaymentsForm,
                                   PayPalEncryptedPaymentsForm)


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
                if k.startswith('amount_'):
                    self.fields[k] = forms.IntegerField(
                        widget=forms.widgets.HiddenInput())
                    has_multiple_items = True
                elif  k.startswith('item_name_'):
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
