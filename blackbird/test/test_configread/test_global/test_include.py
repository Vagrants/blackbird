# -*- coding: utf-8 -*-

import os

import nose.tools

import blackbird.utils.configread


class TestGlobalIncludeSection(object):

    def __init__(self):
        infile = (
            '[global]',
            'user = nobody',
            'group = nobody'
        )
        self.test_config = blackbird.utils.configread.ConfigReader(
            infile=infile
        )

    def test_abs_path(self):
        test_value = '/etc/blackbird/conf.d/*.cfg'
        nose.tools.eq_(
            test_value,
            self.test_config._get_global_include_abs_path(
                test_value
            )
        )

    def test_relative_path(self):
        test_value = './blackbird/*.cfg'
        nose.tools.ok_(
            os.path.isabs(
                self.test_config._get_global_include_abs_path(
                    test_value
                )
            )
        )

    def test_abs_dir(self):
        test_value = os.path.join(
            __file__, '../../etc/'
        )
        test_value = os.path.abspath(test_value)
        test_value = self.test_config._get_global_include_abs_path(
            test_value
        )
        nose.tools.ok_(
            os.path.isabs(test_value) and
            test_value.endswith('*')
        )

    def test_relative_dir(self):
        test_value = self.test_config._get_global_include_abs_path(
            './'
        )
        nose.tools.ok_(
            os.path.isabs(test_value) and
            test_value.endswith('*')
        )
