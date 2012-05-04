from django import forms
from django.utils.translation import ugettext_lazy as _


class EwayAuForm(forms.Form):
    EWAY_ACCESSCODE = forms.CharField(widget=forms.HiddenInput())
    EWAY_CARDNAME = forms.CharField(label=_("Name"))
    EWAY_CARDNUMBER = forms.CharField(label=_("Credit card number"))
    EWAY_CARDMONTH = forms.CharField(label=_("Expiration month"))
    EWAY_CARDYEAR = forms.CharField(label=_("Expiration year"))
    EWAY_CARDCVN = forms.CharField(label=_("CVN"))
