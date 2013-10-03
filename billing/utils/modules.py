import sys
import os
import pkgutil

def get_module_names(package_name):
    package = sys.modules[package_name]
    pkgpath = os.path.dirname(package.__file__)
    return [name for _, name, _ in pkgutil.iter_modules([pkgpath])]

def get_models(module):
    from django.db import models
    try:
        attrlist = module.__all__
    except AttributeError:
        attrlist = dir(module)
    for attr in attrlist:
        obj = getattr(module, attr)
        try:
            if issubclass(obj, models.Model):
                yield obj
        except TypeError:
            pass
