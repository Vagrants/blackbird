#!/usr/bin/env python
# -*- encodig: utf-8 -*-
"""
These classes are used by other tests.
"""

import glob
import os
import shutil
import tempfile

from utils import configread


class ConfigReaderTestBase(object):
    """
    Define intersection in this class.
    For example, setup, teardown and defaults.cfg(for test)...
    Other class that inhelited this class is be able to
    use setup decorator as follow:

    class TestSweet(BaseTest):

        *snip*

        @setup(BaseTest.setup,BaseTest.teardown)
        def testcase1(self):
            print self.value1
    """

    def __init__(self):
        self.cfg_line = None
        self.cfg_file = None
        self.dir = None
        self.configreader = None

    def setup(self):
        """
        Define the following values for the test:
            * defaults.cfg(line of lists)
            * defaults.cfg(named file)
            * temporary directory
                + e.g used when reading include
            * basic configreader instance
        """

        self.cfg_line = (
            '[global]',
            'log_file = tmp/log/hoghoge.log',
            'pid_file = tmp/hogehoge.pid',
            '[localhost_redis]',
            'host = 127.0.0.1',
            'port = 6739',
            'module = redis'
        )

        self.dir = os.path.abspath('tests/tmp')
        os.mkdir(self.dir)

        self.cfg_file = tempfile.NamedTemporaryFile(mode='r+',
                                                    suffix='.cfg',
                                                    dir=self.dir
                                                    )
        self.cfg_file.writelines(self.cfg_line)
        self.cfg_file.seek(0)

        self.configreader = configread.ConfigReader(self.cfg_file)

    def teardown(self):
        u"""
        Remove temporary files and directories.
        """

        # remove config file for test.
        self.cfg_file.close()

        # remove dir for test.
        try:
            os.removedirs(self.dir)
        except OSError:
            err_message = (
                "tests/tmp directory is not empty. "
                "Removed forcibly tests/tmp."
            )
            print ''.join(err_message)

            # chmod 0777 tests/tmp/*
            for dir in glob.glob(os.path.join(self.dir, '*')):
                os.chmod(dir, 0777)

            # rm -fr tests/tmp
            shutil.rmtree(self.dir)
