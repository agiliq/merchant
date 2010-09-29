
import re
import datetime

CARD_COMPANIES = {
    'visa'               : '^4\d{12}(\d{3})?$',
    'master'             : '^(5[1-5]\d{4}|677189)\d{10}$',
    'discover'           : '^(6011|65\d{2})\d{12}$',
    'american_express'   : '^3[47]\d{13}$',
    'diners_club'        : '^3(0[0-5]|[68]\d)\d{11}$',
    'jcb'                : '^35(28|29|[3-8]\d)\d{12}$',
    'switch'             : '^6759\d{12}(\d{2,3})?$',  
    'solo'               : '^6767\d{12}(\d{2,3})?$',
    'dankort'            : '^5019\d{12}$',
    'maestro'            : '^(5[06-8]|6\d)\d{10,17}$',
    'forbrugsforeningen' : '^600722\d{10}$',
    'laser'              : '^(6304|6706|6771|6709)\d{8}(\d{4}|\d{6,7})?$'
}

class CreditCard(object):
    def __init__(self, first_name=None, last_name=None, month=None, year=None, number=None, card_type=None, verification_value=None):
        self.first_name = first_name
        self.last_name = last_name
        self.month = int(month)
        self.year = int(year)
        self.number = number
        self.card_type = card_type or self.get_card_type()
        self.verification_value = verification_value
    
    def get_card_type(self):
        """Find the credit card type for the given card number"""
        for company, pattern in CARD_COMPANIES.items():
            # Maestro regexp overlaps with the MasterCard regexp (IIRC).
            if not company == 'maestro' and re.match(pattern, self.number):
                return company
        
        if re.match(CARD_COMPANIES['maestro'], self.number):
            return 'maestro' 
        else:
            return None
    
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
    