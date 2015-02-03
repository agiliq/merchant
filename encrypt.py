#!/usr/bin/env python

"""
Add merchant settings as encryped env vars to .travis.yml
"""

from __future__ import print_function

import os

from django.core.management import setup_environ

from example.settings import local
setup_environ(local)

from django.conf import settings

from formencode.variabledecode import variable_encode

env_dict = variable_encode(settings.MERCHANT_SETTINGS, prepend='MERCHANT', dict_char='__')
for k, v in env_dict.iteritems():
    print('adding %s' % (k))
    os.system('travis encrypt %s="%s" --add env.global' % (k, v))
