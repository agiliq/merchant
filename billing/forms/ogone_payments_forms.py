from django import forms


class OgonePaymentsForm(forms.Form):
    # Required
    PSPID = forms.CharField(widget=forms.HiddenInput, required=True)
    ORDERID = forms.CharField(widget=forms.HiddenInput, required=True)  # REF
    AMOUNT = forms.CharField(widget=forms.HiddenInput, required=True)  # * 100
    CURRENCY = forms.CharField(widget=forms.HiddenInput, required=True)
    LANGUAGE = forms.CharField(widget=forms.HiddenInput, required=True)  # client language
    # Layout
    TITLE = forms.CharField(widget=forms.HiddenInput, required=False)
    LOGO = forms.CharField(widget=forms.HiddenInput, required=False)
    # Post-payment redirection
    ACCEPTURL = forms.CharField(widget=forms.HiddenInput, required=False)
    DECLINEURL = forms.CharField(widget=forms.HiddenInput, required=False)
    EXCEPTIONURL = forms.CharField(widget=forms.HiddenInput, required=False)
    CANCELURL = forms.CharField(widget=forms.HiddenInput, required=False)
    BACKURL = forms.CharField(widget=forms.HiddenInput, required=False)
    # Miscellanous
    HOMEURL = forms.CharField(widget=forms.HiddenInput, required=False)
    CATALOGURL = forms.CharField(widget=forms.HiddenInput, required=False)
    CN = forms.CharField(widget=forms.HiddenInput, required=False)
    EMAIL = forms.CharField(widget=forms.HiddenInput, required=False)
    PM = forms.CharField(widget=forms.HiddenInput, required=False)
    BRAND = forms.CharField(widget=forms.HiddenInput, required=False)
    OWNERZIP = forms.CharField(widget=forms.HiddenInput, required=False)
    OWNERADDRESS = forms.CharField(widget=forms.HiddenInput, required=False)
    OWNERADDRESS2 = forms.CharField(widget=forms.HiddenInput, required=False)
    SHASIGN = forms.CharField(widget=forms.HiddenInput, required=False)
    ALIAS = forms.CharField(widget=forms.HiddenInput, required=False)
    ALIASUSAGE = forms.CharField(widget=forms.HiddenInput, required=False)
    ALIASOPERATION = forms.CharField(widget=forms.HiddenInput, required=False)
    COM = forms.CharField(widget=forms.HiddenInput, required=False)
    COMPLUS = forms.CharField(widget=forms.HiddenInput, required=False)
    PARAMPLUS = forms.CharField(widget=forms.HiddenInput, required=False)
    USERID = forms.CharField(widget=forms.HiddenInput, required=False)
    CREDITCODE = forms.CharField(widget=forms.HiddenInput, required=False)
