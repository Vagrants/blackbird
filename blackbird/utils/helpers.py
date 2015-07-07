# -*- coding: utf-8 -*-
u"""Useful functions that are used by other modules."""

import imp
import sys
from blackbird.utils.error import BlackbirdError


def helper_import(module_name, class_name=None):
    """
    Return class or module object.
    if the argument is only a module name and return a module object.
    if the argument is a module and class name, and return a class object.
    """
    try:
        module = __import__(module_name, globals(), locals(), [class_name])
    except (BlackbirdError, ImportError) as error:
        raise BlackbirdError(
            'can not load {0} module [{1}]'
            ''.format(module_name, str(error))
        )

    if not class_name:
        return module
    else:
        try:
            return getattr(module, class_name)
        except:
            return False


def global_import(mod_name):
    """
    This function search sys.path[1:], return specified module.
    sys.path[1:] means the directories other than current directory('./').

    'mod_name' as an argument is string type object.
    """
    mod_tuple = imp.find_module(mod_name, sys.path[1:])
    mod = imp.load_module(mod_name, mod_tuple[0], mod_tuple[1], mod_tuple[2])

    return mod
