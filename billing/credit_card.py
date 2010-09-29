
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
        self.card_type = card_type or self.get_card_type(number)
        self.verification_value = verification_value
    
    def get_card_type(self, number):
        for company, pattern in CARD_COMPANIES.items():
            # Right now the Maestro regexp overlaps with the MasterCard regexp (IIRC).
            if not company == 'maestro' and re.match(number, pattern):
                return company
        return 'maestro' if re.match(number, CARD_COMPANIES['maestro']) else None
    
    def is_luhn_valid(self):
        # Checks the validity of a card number by use of the the Luhn Algorithm. 
        # Please see http://en.wikipedia.org/wiki/Luhn_algorithm for details.
        num = [int(x) for x in str(self.number)]
        return not sum(num[::-2] + [sum(divmod(d * 2, 10)) for d in num[-2::-2]]) % 10
    
    def is_expired(self):
        return datetime.date.today() > datetime.date(self.year, self.month, 1)
    
    def valid_essential_attributes(self):
        return self.first_name and \
               self.last_name and \
               self.month and \
               self.year and \
               self.number and \
               self.verification_value and True
    
    def is_valid(self):
        return self.is_luhn_valid() and \
               not self.is_expired() and \
               self.valid_essential_attributes()
    
    @property
    def expire_date(self):
        return '%02d-%04d' % (self.month, self.year)