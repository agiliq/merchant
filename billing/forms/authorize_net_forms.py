from django import forms


class AuthorizeNetDPMForm(forms.Form):
    x_card_num = forms.CharField(max_length=16, label="Credit Card #")
    x_exp_date = forms.CharField(max_length=5, label="Exp Date (mm/yy)")
    x_card_code = forms.CharField(max_length=4, label="CVV")

    x_first_name = forms.CharField(max_length=50, label="First Name")
    x_last_name = forms.CharField(max_length=50, label="Last Name")

    x_address = forms.CharField(widget=forms.Textarea, max_length=60, label="Address")
    x_city = forms.CharField(max_length=40, label="City")
    x_state = forms.CharField(max_length=40, label="State")
    x_zip = forms.CharField(max_length=20, label="Zip")
    x_country = forms.CharField(max_length=60, label="Country")

    x_amount = forms.CharField(label="Amount (in USD)")

    x_login = forms.CharField(widget=forms.HiddenInput(), required=False)
    x_fp_sequence = forms.CharField(widget=forms.HiddenInput(), required=False)
    x_fp_timestamp = forms.CharField(widget=forms.HiddenInput())
    x_fp_hash = forms.CharField(widget=forms.HiddenInput())
    x_type = forms.CharField(widget=forms.HiddenInput())

    x_relay_response = forms.CharField(initial="TRUE", widget=forms.HiddenInput())
