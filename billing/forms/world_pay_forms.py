from django import forms
from hashlib import md5
from django.conf import settings


class WPHostedPaymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(WPHostedPaymentForm, self).__init__(*args, **kwargs)
        if self.initial:
            self.initial["signatureFields"] = self.initial.get("signatureFields") or "instId:amount:cartId"
            signature_fields = self.initial["signatureFields"].split(":")
            hash_str = ""
            for field in signature_fields:
                hash_str += "%s" % self.initial[field]
                if not signature_fields.index(field) == len(signature_fields) - 1:
                    hash_str += ":"
            md5_hash = md5("%s:%s" % (settings.MERCHANT_SETTINGS["world_pay"]["MD5_SECRET_KEY"],
                                     hash_str)).hexdigest()
            self.initial["signature"] = self.initial.get("signature") or md5_hash

    # recurring(future pay) parameters
    futurePayType = forms.CharField(widget=forms.HiddenInput(), required=False)
    intervalUnit = forms.CharField(widget=forms.HiddenInput(), required=False)
    intervalMult = forms.CharField(widget=forms.HiddenInput(), required=False)
    option = forms.CharField(widget=forms.HiddenInput(), required=False)
    noOfPayments = forms.CharField(widget=forms.HiddenInput(), required=False)
    normalAmount = forms.CharField(widget=forms.HiddenInput(), required=False)
    startDelayUnit = forms.CharField(widget=forms.HiddenInput(), required=False)
    startDelayMult = forms.CharField(widget=forms.HiddenInput(), required=False)

    instId = forms.CharField(widget=forms.HiddenInput)
    cartId = forms.CharField(widget=forms.HiddenInput)
    amount = forms.DecimalField(widget=forms.HiddenInput)
    currency = forms.CharField(widget=forms.HiddenInput, initial="USD")
    desc = forms.CharField(widget=forms.HiddenInput)
    testMode = forms.CharField(widget=forms.HiddenInput)
    signatureFields = forms.CharField(widget=forms.HiddenInput)
    signature = forms.CharField(widget=forms.HiddenInput)

    #override Country field
    # country = CountryField(initial="AU")
