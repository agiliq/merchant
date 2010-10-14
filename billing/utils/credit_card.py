
import re
import datetime

class InvalidCard(Exception):
    pass

class CreditCard(object):
    # The regexp attribute should be overriden by the subclasses.
    # Attribute value should be a regexp instance
    regexp = None
    # Has to be set by the user after calling `validate_card`
    # method on the gateway
    card_type = None

    def __init__(self, **kwargs):
        self.first_name = kwargs["first_name"]
        self.last_name = kwargs["last_name"]
        self.month = int(kwargs["month"])
        self.year = int(kwargs["year"])
        self.number = kwargs["number"]
        self.verification_value = kwargs["verification_value"]
    
    def is_luhn_valid(self):
        """Checks the validity of card number by using Luhn Algorithm. 
        Please see http://en.wikipedia.org/wiki/Luhn_algorithm for details."""
        num = [int(x) for x in str(self.number)]
        return not sum(num[::-2] + [sum(divmod(d * 2, 10)) for d in num[-2::-2]]) % 10
    
    def is_expired(self):
        """Check whehter the credit card is expired or not"""
        return datetime.date.today() > datetime.date(self.year, self.month, 1)
    
    def valid_essential_attributes(self):
        """Validate that all the required attributes of card are given"""
        return self.first_name and \
               self.last_name and \
               self.month and \
               self.year and \
               self.number and \
               self.verification_value and True
    
    def is_valid(self):
        """Check the validity of the card"""
        return self.is_luhn_valid() and \
               not self.is_expired() and \
               self.valid_essential_attributes()
    
    @property
    def expire_date(self):
        """Returns the expiry date of the card in MM-YYYY format"""
        return '%02d-%04d' % (self.month, self.year)
    
    @property
    def name(self):
        """Concat first name and last name of the card holder"""
        return '%s %s' % (self.first_name, self.last_name)


class Visa(CreditCard):
    regexp = re.compile('^4\d{12}(\d{3})?$')

class MasterCard(CreditCard):
    regexp = re.compile('^(5[1-5]\d{4}|677189)\d{10}$')

class Discover(CreditCard):
    regexp = re.compile('^(6011|65\d{2})\d{12}$')

class AmericanExpress(CreditCard):
    regexp = re.compile('^3[47]\d{13}$')

class DinersClub(CreditCard):
    regexp = re.compile('^3(0[0-5]|[68]\d)\d{11}$')

class JCB(CreditCard):
    regexp = re.compile('^35(28|29|[3-8]\d)\d{12}$')

class Switch(CreditCard):
    # Debit Card
    regexp = re.compile('^6759\d{12}(\d{2,3})?$')

class Solo(CreditCard):
    # Debit Card
    regexp = re.compile('^6767\d{12}(\d{2,3})?$')

class Dankort(CreditCard):
    # Debit cum Credit Card
    regexp = re.compile('^5019\d{12}$')

class Maestro(CreditCard):
    # Debit Card
    regexp = re.compile('^(5[06-8]|6\d)\d{10,17}$')

class Forbrugsforeningen(CreditCard):
    regexp = re.compile('^600722\d{10}$')

class Laser(CreditCard):
    # Debit Card
    regexp = re.compile('^(6304|6706|6771|6709)\d{8}(\d{4}|\d{6,7})?$')

# A few helpful (probably) attributes
all_credit_cards = [Visa, MasterCard, Discover, AmericanExpress,
                    DinersClub, JCB]

all_debit_cards  = [Switch, Solo, Dankort, Maestro,
                    Forbrugsforeningen, Laser]

all_cards = all_credit_cards + all_debit_cards
