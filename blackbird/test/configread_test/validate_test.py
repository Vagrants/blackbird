# -*- coding: utf-8 -*-
"""
Tests for validation of each section other than [global].
"""

import os
import tempfile

from nose.tools import assert_false, ok_

from blackbird.test.configread_test.base import TmpPluginBase
from blackbird.utils.configread import ConfigReader


class TestGetModule(TmpPluginBase):
    """
    ConfigReader._get_modules() tests.
    """

    def extend_module_dir_test(self):
        plugin = self.create_plugins()
        check_value = plugin[0]

        cfg_lines = (
            '[global]',
            'module_dir = {0}'.format(self.tmp_dir),
        )

        cfg_reader = ConfigReader(infile=cfg_lines)
        modules = cfg_reader._get_modules()

        ok_(
            check_value in modules,
            msg='{0}'.format(modules)
        )

    def not_implement_validator_test(self):
        cfg_lines = (
            '[global]',
            'module_dir = {0}'.format(self.tmp_dir),
        )
        plugin_lines = (
            'class ConcreteJob(object):\n',
            '    pass\n',
            'class InValidValidator(object):\n',
            '    pass\n',
        )

        plugin = tempfile.NamedTemporaryFile(
            dir=self.tmp_dir,
            suffix='.py'
        )
        plugin.writelines(plugin_lines)
        plugin.seek(0)

        cfg_reader = ConfigReader(infile=cfg_lines)
        modules = cfg_reader._get_modules()
        check_value = os.path.split(plugin.name)[1]
        check_value = check_value.split('.')[0]

        assert_false(
            check_value in modules,
            msg='{0}'.format(modules)
        )


class TestGetRawSpecs(TmpPluginBase):
    """
    ConfigReader._get_raw_specs() tests.
    """

    def normal_test(self):
        plugin = self.create_plugins()
        check_value = plugin[0]

        cfg_lines = (
            '[global]',
            'module_dir = {0}'.format(self.tmp_dir),
            '[temporary]',
            'module = {0}'.format(check_value),
        )

        cfg_reader = ConfigReader(infile=cfg_lines)
        raw_specs = cfg_reader._get_raw_specs(cfg_reader.config)

        ok_(
            check_value in raw_specs,
            msg='ConfigReader has {0} as specs'.format(raw_specs)
        )


class TestCreateSpecs(TmpPluginBase):
    """
    ConfigReader._create_specs() tests.
    """
    def normal_test(self):
        plugin = self.create_plugins()
        mod_name = plugin[0]
        section_name = 'temporary'

        cfg_lines = (
            '[global]',
            'module_dir = {0}'.format(self.tmp_dir),
            '[{0}]'.format(section_name),
            'module = {0}'.format(mod_name),
        )

        cfg_reader = ConfigReader(infile=cfg_lines)

        spec_lines = cfg_reader._get_raw_specs(cfg_reader.config)
        spec_lines = spec_lines[mod_name]
        spec = cfg_reader._configspec_factory(
            '{0}'.format(section_name),
            mod_name,
            spec_lines,
        )

        ok_(
            section_name in spec,
            msg='Failed creation spec(for validation)'
        )
