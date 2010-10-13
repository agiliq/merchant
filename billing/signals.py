from django.dispatch import Signal

transaction_started = Signal()
payment_was_succesful = Signal()
payment_was_unsuccesful = Signal()
