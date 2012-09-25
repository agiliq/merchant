

def require(d, *args):
    for arg in args:
        if arg not in d:
            raise TypeError('Missing required parameter: %s' % (arg))
