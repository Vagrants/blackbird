# -*- coding: utf-8 -*-

import os

import nose.tools

import blackbird.utils.configread


class TestConfigReaderAddDefaultModuleDir(object):

    def test_no_module_dir(self):
        infile = (
            '[global]',
            ''
        )
        test_config = blackbird.utils.configread.ConfigReader(
            infile=infile
        )
        default_module_dir = os.path.join(
            os.path.abspath(os.path.curdir),
            'plugins'
        )
        module_dirs = test_config.config['global']['module_dir']
        nose.tools.ok_(
            (
                len(module_dirs) == 1
            ) and
            (
                module_dirs[0] == default_module_dir
            )
        )

    def test_custom_module_dir(self):
        optional_module_dir = '/opt/blackbird/plugins'
        infile = (
            '[global]',
            'module_dir = {0}'.format(optional_module_dir)
        )
        test_config = blackbird.utils.configread.ConfigReader(
            infile=infile
        )
        module_dirs = test_config.config['global']['module_dir']
        print module_dirs
        nose.tools.ok_(
            (
                len(module_dirs) == 2
            ) and
            (
                module_dirs[1] == optional_module_dir
            )
        )
