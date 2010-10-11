
from django import forms

class RBSHostedPaymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RBSHostedPaymentForm, self).__init__(*args, **kwargs)
    
    # recurring(future pay) parameters
    futurePayType  = forms.CharField(widget=forms.HiddenInput(), required=False)
    intervalUnit   = forms.CharField(widget=forms.HiddenInput(), required=False)
    intervalMult   = forms.CharField(widget=forms.HiddenInput(), required=False)
    option         = forms.CharField(widget=forms.HiddenInput(), required=False)
    noOfPayments   = forms.CharField(widget=forms.HiddenInput(), required=False)
    normalAmount   = forms.CharField(widget=forms.HiddenInput(), required=False)
    startDelayUnit = forms.CharField(widget=forms.HiddenInput(), required=False)
    startDelayMult = forms.CharField(widget=forms.HiddenInput(), required=False)

    instId          = forms.CharField(widget=forms.HiddenInput)
    cartId          = forms.CharField(widget=forms.HiddenInput)
    amount          = forms.DecimalField(widget=forms.HiddenInput)
    currency        = forms.CharField(widget=forms.HiddenInput, initial="USD")
    desc            = forms.CharField(widget=forms.HiddenInput)
    testMode        = forms.CharField(widget=forms.HiddenInput)
    signatureFields = forms.CharField(widget=forms.HiddenInput)
    signature       = forms.CharField(widget=forms.HiddenInput)
    
    #override Country field
    # country = CountryField(initial="AU")
 