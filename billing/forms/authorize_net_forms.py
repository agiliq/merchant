from django import forms

class AuthorizeNetDPMForm(forms.Form):
    x_login = forms.CharField(widget=forms.HiddenInput(), required=False)
    x_fp_sequence = forms.CharField(widget=forms.HiddenInput(), required=False)
    x_fp_timestamp = forms.CharField(widget=forms.HiddenInput())
    x_fp_hash = forms.CharField(widget=forms.HiddenInput())
    x_type = forms.CharField(widget=forms.HiddenInput())

    x_relay_response = forms.BooleanField(initial=True, widget=forms.HiddenInput())

    x_first_name = forms.CharField(max_length=50, label="First Name")
    x_last_name = forms.CharField(max_length=50, label="Last Name")

    x_amount = forms.CharField(label="Amount (in USD)")
