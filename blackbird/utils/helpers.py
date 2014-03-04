# -*- coding: utf-8 -*-
u"""Useful functions that are used by other modules."""

import imp
import sys


def helper_import(module_name, class_name=None):
    """
    Return class or module object.
    if the argument is only a module name and return a module object.
    if the argument is a module and class name, and return a class object.
    """
    module = __import__(module_name, globals(), locals(), [class_name])

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
