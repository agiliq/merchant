from django.dispatch import Signal

transaction_started = Signal()
payment_was_successful = Signal()
payment_was_unsuccessful = Signal()
