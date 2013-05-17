import random, string


def randomword(word_len):
	rstr = string.lowercase + string.digits
	return ''.join(random.sample(rstr, word_len))
