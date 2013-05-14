# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4
"""
Example usage:

from billing.utils.credit_card import Visa

product = PaylanePaymentProduct(description='Some description')
customer_address = PaylanePaymentCustomerAddress(street_house='',city='',state='',zip_code='',country_code='PT')
customer = PaylanePaymentCustomer(name='',email='',ip_address='127.0.0.1',address=customer_address)
pp = PaylanePayment(credit_card=Visa(),customer=customer,amount=0.01,product=product)
"""


class PaylanePaymentCustomerAddress(object):
    def __init__(self, street_house=None, city=None, state=None, zip_code=None, country_code=None):
        self.street_house = street_house
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country_code = country_code


class PaylanePaymentCustomer(object):
    def __init__(self, name=None, email=None, ip_address=None, address=None):
        self.name = name
        self.email = email
        self.ip_address = ip_address
        self.address = address


class PaylanePaymentProduct(object):
    def __init__(self, description=None):
        self.description = description


class PaylanePayment(object):
    def __init__(self, credit_card=None, customer=None, amount=0.0, product=None):
        self.credit_card = credit_card
        self.customer = customer
        self.amount = amount
        self.product = product


class PaylaneError(object):
    ERR_INVALID_ACCOUNT_HOLDER_NAME = 312
    ERR_INVALID_CUSTOMER_NAME = 313
    ERR_INVALID_CUSTOMER_EMAIL = 314
    ERR_INVALID_CUSTOMER_ADDRESS = 315
    ERR_INVALID_CUSTOMER_CITY = 316
    ERR_INVALID_CUSTOMER_ZIP = 317
    ERR_INVALID_CUSTOMER_STATE = 318
    ERR_INVALID_CUSTOMER_COUNTRY = 319
    ERR_INVALID_AMOUNT = 320
    ERR_AMOUNT_TOO_LOW = 321
    ERR_INVALID_CURRENCY_CODE = 322
    ERR_INVALID_CUSTOMER_IP = 323
    ERR_INVALID_DESCRIPTION = 324
    ERR_INVALID_ACCOUNT_COUNTRY = 325
    ERR_INVALID_BANK_CODE = 326
    ERR_INVALID_ACCOUNT_NUMBER = 327
    ERR_UNKNOWN_PAYMENT_METHOD = 405
    ERR_TOO_MANY_PAYMENT_METHODS = 406
    ERR_CANNOT_CAPTURE_LATER = 407
    ERR_FEATURE_NOT_AVAILABLE = 408
    ERR_CANNOT_OVERRIDE_FEATURE = 409
    ERR_UNSUPPORTED_PAYMENT_METHOD = 410
    ERR_INVALID_CARD_NUMBER_FORMAT = 411
    ERR_INVALID_EXPIRATION_YEAR = 412
    ERR_INVALID_EXPIRATION_MONTH = 413
    ERR_EXPIRATION_YEAR_PAST = 414
    ERR_CARD_EXPIRED = 415
    ERR_INVALID_CARD_NAME = 417
    ERR_INVALID_CARDHOLDER_NAME = 418
    ERR_INVALID_CARDHOLDER_EMAIL = 419
    ERR_INVALID_CARDHOLDER_ADDRESS = 420
    ERR_INVALID_CARDHOLDER_CITY = 421
    ERR_INVALID_CARDHOLDER_ZIP = 422
    ERR_INVALID_CARDHOLDER_STATE = 423
    ERR_INVALID_CARDHOLDER_COUNTRY = 424
    ERR_INVALID_AMOUNT2 = 425
    ERR_AMOUNT_TOO_LOW2 = 426
    ERR_INVALID_CURRENCY_CODE2 = 427
    ERR_INVALID_CLIENT_IP = 428
    ERR_INVALID_DESCRIPTION2 = 429
    ERR_UNKNOWN_CARD_TYPE_NUMBER = 430
    ERR_INVALID_CARD_ISSUE_NUMBER = 431
    ERR_CANNOT_FRAUD_CHECK = 432
    ERR_INVALID_AVS_LEVEL = 433
    ERR_INVALID_SALE_ID = 441
    ERR_SALE_AUTHORIZATION_NOT_FOUND = 442
    ERR_CAPTURE_EXCEEDS_AUTHORIZATION_AMOUNT = 443
    ERR_TRANSACTION_LOCK = 401
    ERR_GATEWAY_PROBLEM = 402
    ERR_CARD_DECLINED = 403
    ERR_CURRENCY_NOT_ALLOWED = 404
    ERR_CARD_CODE_INVALID = 416
    ERR_CARD_CODE_MANDATORY = 470
    ERR_INVALID_SALE_ID = 471
    ERR_INVALID_RESALE_AMOUNT = 472
    ERR_RESALE_AMOUNT_TOO_LOW = 473
    ERR_INVALID_RESALE_CURRENCY = 474
    ERR_INVALID_RESALE_DESCRIPTION = 475
    ERR_SALE_ID_NOT_FOUND = 476
    ERR_RESALE_WITH_CHARGEBACK = 477
    ERR_CANNOT_RESALE_SALE = 478
    ERR_RESALE_CARD_EXPIRED = 479
    ERR_RESALE_WITH_REVERSAL = 480
    ERR_CANNOT_REFUND_SALE = 488
    ERR_INTERNAL_ERROR = 501
    ERR_GATEWAY_ERROR = 502
    ERR_METHOD_NOT_ALLOWED = 503
    ERR_INACTIVE_MERCHANT = 505
    ERR_FRAUD_DETECTED = 601
    ERR_BLACKLISTED_NUMBER = 611
    ERR_BLACKLISTED_COUNTRY = 612
    ERR_BLACKLISTED_CARD_NUMBER = 613
    ERR_BLACKLISTED_CUSTOMER_COUNTRY = 614
    ERR_BLACKLISTED_CUSTOMER_EMAIL = 615
    ERR_BLACKLISTED_CUSTOMER_IP = 616

    def __init__(self, error_code, description, acquirer_error=None, acquirer_description=None):
        self.FRAUD_ERRORS = [self.ERR_FRAUD_DETECTED, self.ERR_BLACKLISTED_NUMBER,
                            self.ERR_BLACKLISTED_COUNTRY, self.ERR_BLACKLISTED_CARD_NUMBER,
                            self.ERR_BLACKLISTED_CUSTOMER_COUNTRY,
                            self.ERR_BLACKLISTED_CUSTOMER_EMAIL,
                            self.ERR_BLACKLISTED_CUSTOMER_IP]
        self.error_code = error_code
        self.description = description
        self.acquirer_error = acquirer_error
        self.acquirer_description = acquirer_description

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Error Code: %s (%s). Acquirer Error: %s (%s)' % (self.error_code,
            self.description,
            self.acquirer_error,
            self.acquirer_description)

    def __unicode__(self):
        return unicode(str(self))

    @property
    def is_customer_data_error(self):
        """True if error is related to the card/account data the customer provided."""
        return self.error_code in [
                self.ERR_INVALID_ACCOUNT_HOLDER_NAME,
                self.ERR_INVALID_CUSTOMER_NAME,
                self.ERR_INVALID_CUSTOMER_EMAIL,
                self.ERR_INVALID_CUSTOMER_ADDRESS,
                self.ERR_INVALID_CUSTOMER_CITY,
                self.ERR_INVALID_CUSTOMER_ZIP,
                self.ERR_INVALID_CUSTOMER_STATE,
                self.ERR_INVALID_CUSTOMER_COUNTRY,
                self.ERR_INVALID_ACCOUNT_COUNTRY,
                self.ERR_INVALID_BANK_CODE,
                self.ERR_INVALID_ACCOUNT_NUMBER,
                self.ERR_INVALID_CARD_NAME,
                self.ERR_INVALID_CARDHOLDER_NAME,
                self.ERR_INVALID_CARDHOLDER_EMAIL,
                self.ERR_INVALID_CARDHOLDER_ADDRESS,
                self.ERR_INVALID_CARDHOLDER_CITY,
                self.ERR_INVALID_CARDHOLDER_ZIP,
                self.ERR_INVALID_CARDHOLDER_STATE,
                self.ERR_INVALID_CARDHOLDER_COUNTRY,
            ]

    @property
    def is_card_data_error(self):
        """True if error is related to the card data the customer provided."""
        return self.error_code in [
                self.ERR_UNKNOWN_CARD_TYPE_NUMBER,
                self.ERR_INVALID_CARD_ISSUE_NUMBER,
            ]

    @property
    def was_card_declined(self):
        """True if this error is related to the card being declined for some reason."""
        return self.error_code in [
                self.ERR_CARD_DECLINED,
            ] or self.is_card_expired

    @property
    def is_card_expired(self):
        """True if this error is related to card expiration."""
        return self.error_code in [
                self.ERR_CARD_EXPIRED,
                self.ERR_RESALE_CARD_EXPIRED,
            ]

    @property
    def is_recurring_impossible(self):
        """Whether this error should nullify a recurring transaction."""
        return self.error_code in [
                self.ERR_CARD_DECLINED,
                self.ERR_CARD_CODE_INVALID,
                self.ERR_CARD_CODE_MANDATORY,
                self.ERR_INVALID_SALE_ID,
                self.ERR_INVALID_RESALE_AMOUNT,
                self.ERR_RESALE_AMOUNT_TOO_LOW,
                self.ERR_SALE_ID_NOT_FOUND,
                self.ERR_RESALE_WITH_CHARGEBACK,
                self.ERR_CANNOT_RESALE_SALE,
                self.ERR_RESALE_CARD_EXPIRED,
                self.ERR_RESALE_WITH_REVERSAL,
            ]

    @property
    def is_fatal(self):
        """Whether this is a fatal error that, in principle, cannot be retried."""
        return self.error_code == self.ERR_CANNOT_REFUND_SALE or self.error_code >= 500

    @property
    def is_fraud(self):
        """Whether this is a fraud fatal error."""
        return self.error_code in self.FRAUD_ERRORS

    @property
    def can_retry_later(self):
        """Whether this resale fatal error can disappear in the future."""
        return self.error_code in [
                self.ERR_INTERNAL_ERROR,
                self.ERR_GATEWAY_ERROR,
            ]
