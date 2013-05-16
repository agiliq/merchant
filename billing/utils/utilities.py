import random, string

class Bunch(dict):
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self

def randomword(word_len):
	rstr = string.lowercase + string.digits
	return ''.join(random.sample(rstr, word_len))
