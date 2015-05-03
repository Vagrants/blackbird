# -*- coding: utf-8 -*-
"""
configread.JobObserver tests
"""

from nose.tools import ok_, raises

from blackbird.test.configread_test.base import TmpPluginBase
from blackbird.utils.configread import ConfigReader
from blackbird.utils.configread import JobObserver
from blackbird.utils.configread import NotSupportedError
from blackbird.utils.configread import ConfigMissingValue


class TestRegisterJobs(TmpPluginBase):
    """
    ConfigReader._register_jobs() tests.
    This method notify some objects to registerd observer.
    In this case, ConfigReader object is subject,
    and notifies the jobs(plugins) that written in config file.
    """

    def normal_test(self):
        """
        Create temporary plugin and register it as jobs.
        """

        plugin = self.create_plugins()
        check_value = plugin[0]

        cfg_lines = (
            '[global]',
            'module_dir = {0}'.format(self.tmp_dir),
            '[temporary]',
            'module = {0}'.format(check_value)
        )

        observer = JobObserver()
        cfg_reader = ConfigReader(infile=cfg_lines, observers=observer)

        ok_(
            check_value in observer.jobs,
            msg='JobObserver.jobs: {0}'.format(observer.jobs)
        )

    @raises(ConfigMissingValue)
    def missing_module_value_test(self):
        """
        be specified 'module' value in config file.
        """
        cfg_lines = (
            '[global]',
            '',
            '[for_test]',
            '',
        )
        ok_(ConfigReader(infile=cfg_lines))

    @raises(NotSupportedError)
    def not_support_plugin_test(self):
        """
        specify plugin name that doesn't exists to module value in config file.
        """
        cfg_lines = (
            '[global]',
            '',
            '[for_test]',
            'module = NotExistsPlugin'
        )
        ok_(ConfigReader(infile=cfg_lines))
