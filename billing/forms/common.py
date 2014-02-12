from django import forms

from billing.utils.credit_card import CreditCard, CardNotSupported


class CreditCardFormBase(forms.Form):
    """
    Base class for a simple credit card form which provides some utilities like
    'get_credit_card' to return a CreditCard instance.

    If you pass the gateway as a keyword argument to the constructor,
    the gateway.validate_card method will be used in form validation.

    This class must be subclassed to provide the actual fields to be used.
    """

    def __init__(self, *args, **kwargs):
        self.gateway = kwargs.pop('gateway', None)
        super(CreditCardFormBase, self).__init__(*args, **kwargs)

    def get_credit_card(self):
        """
        Returns a CreditCard from the submitted (cleaned) data.

        If gateway was passed to the form constructor, the gateway.validate_card
        method will be called - which can throw CardNotSupported, and will also
        add the attribute 'card_type' which is the CreditCard subclass if it is
        successful.
        """
        card = CreditCard(**self.cleaned_data)
        if self.gateway is not None:
            self.gateway.validate_card(card)
        return card

    def clean(self):
        cleaned_data = super(CreditCardFormBase, self).clean()
        if self.errors:
            # Don't bother with further validation, it only confuses things
            # for the user to be presented with multiple error messages.
            return cleaned_data
        try:
            credit_card = self.get_credit_card()
            if not credit_card.is_valid():
                raise forms.ValidationError("Credit card details are invalid")
        except CardNotSupported:
            raise forms.ValidationError("This type of credit card is not supported. Please check the number.")
        return cleaned_data
