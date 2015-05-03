# -*- coding: utf-8 -*-
"""Base class of configread module's tests suite"""

import os
import shutil
import tempfile

from blackbird.test.configread_test import TMP_DIR


class ConfigReaderBase(object):
    """
    Base class of general configread tests.
    """
    def setup(self):
        """
        The classes(test suite) which inhelits this class
        call setup()
        before execution all tests.
        """
        self.tmp_dir = TMP_DIR
        os.mkdir(self.tmp_dir)

    def teardown(self):
        """
        The classes(test suite) which inhelits this class
        call teardown()
        after execution all tests.
        """
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


class TmpPluginBase(ConfigReaderBase):
    """
    Using this class when you need to create temporary plugin module.
    """
    def create_plugins(self):
        """
        Creating temporary plugin module.
        Return plugin's name and plugin object(tempfile.NamedTemporaryFile)
        as tuple type.
        """
        plugin = tempfile.NamedTemporaryFile(
            dir=self.tmp_dir,
            suffix='.py'
        )

        plugin_name = os.path.split(plugin.name)[1]
        plugin_name = plugin_name.split('.')[0]

        plugin_lines = (
            'class ConcreteJob(object):\n',
            '    pass\n',
            'class Validator(object):\n',
            '    def __init__(self):\n',
            '        self.spec = (\n',
            '            "[{0}]",\n'.format(plugin_name),
            '            "",\n',
            '        )\n',
        )

        plugin.writelines(plugin_lines)
        plugin.seek(0)

        return (plugin_name, plugin)
