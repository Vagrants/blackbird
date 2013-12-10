#!/usr/bin/env python
# -*- coding:utf-8 -*-
u"""UnitTest: extended_import() in utils/helpers.py"""

import os
import sys
import shutil
from nose.tools import eq_

from utils import helpers

class TestImport(object):
    u"""custom import function"""
    def __init__(self):
        self.module_name = None
        self.class_name = None
        self.tmp_dir = None

    def setup(self):
        u"""
        setup module name and class name.
        And consider virtual package as tests/tmp/pkg/testmodule.py
        """

        self.module_name = 'pkg.testmodule'
        self.class_name = 'TestClass'

        # Create dir and module for test.
        self.tmp_dir = 'tests/tmp'
        os.mkdir(self.tmp_dir)
        pkg_dir = 'tests/tmp/pkg'
        os.mkdir(pkg_dir)
        module_name = 'testmodule.py'

        init_py = open(os.path.join(pkg_dir, '__init__.py'), 'w')
        init_py.close()

        module_str = (
            "class TestClass(object):\n"
            "    pass\n"
        )
        module = open(os.path.join(pkg_dir, module_name), 'w')
        module.write(module_str)
        module.close()

        # Add test directory to sys.path
        sys.path.insert(0, self.tmp_dir)

    def teardown(self):
        u"""
        Remove temporary files and dirs.
        """

        shutil.rmtree(self.tmp_dir)
        sys.path.remove(self.tmp_dir)

    def test_helper_import_for_module(self):
        u"""helper_import(module_name) return "types.ModuleType"."""
        mod = helpers.helper_import(self.module_name)
        eq_(self.module_name, mod.__name__, msg=mod.__name__)

    def test_helper_import_for_class(self):
        u"""helper_import(module_name, class_name) return "types.ClassType"."""
        cls = helpers.helper_import(self.module_name, self.class_name)
        eq_(self.module_name, cls.__module__, msg=cls.__module__)
