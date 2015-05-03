# -*- coding: utf-8 -*-

import os
import glob
import shutil

import nose.tools

import blackbird.utils.configread
import blackbird.utils.error


class TestConfigReaderGetGlobalIncludeAbsPath(object):

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


class TestConfigReaderValidateGlobalInclude(object):

    def __init__(self):
        infile = (
            '[global]',
            'user = nobody',
            'group = nobody'
        )
        self.test_config = blackbird.utils.configread.ConfigReader(
            infile=infile
        )
        self.tmp_dir = os.path.join(
            __file__, '../../tmp'
        )
        self.tmp_dir = os.path.abspath(self.tmp_dir)

    def teardown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_abs_path(self):
        test_value = os.path.join(
            __file__, '../../etc/*'
        )
        test_value = os.path.abspath(test_value)
        nose.tools.ok_(
            self.test_config._validate_global_include(test_value)
        )

    @nose.tools.raises(
        blackbird.utils.error.BlackbirdError
    )
    def test_non_exists_abs_path(self):
        test_value = os.path.join(
            __file__, '../../etc/hogehoge/*'
        )
        test_value = os.path.abspath(test_value)
        self.test_config._validate_global_include(test_value)

    # Using `mkdir` is compelling for like this test.
    @nose.tools.raises(
        blackbird.utils.error.BlackbirdError
    )
    def test_cannot_read_abs_path(self):
        tmp_dir = os.path.join(
            __file__, '../../tmp'
        )
        tmp_dir = os.path.abspath(tmp_dir) + '/'
        os.mkdir(tmp_dir, 0o000)
        self.test_config._validate_global_include(tmp_dir)


class TestConfigReaderMergeIncludes(object):

    def __init__(self):
        self.include_dir = os.path.join(
            os.path.dirname(__file__), '../etc/blackbird/conf.d/'
        )
        infile = (
            '[global]',
            'user = nobody',
            'group = nobody',
            'include = {0}'.format(self.include_dir)
        )
        self.test_config = blackbird.utils.configread.ConfigReader(
            infile=infile
        )

    def teardown(self):
        for config in glob.glob(self.include_dir + '*'):
            os.remove(config)

    def test_merge_one_config(self):
        infile = (
            '[test_statistics]\n',
            'module = statistics'
        )
        with open(
            os.path.join(self.include_dir, 'test_stats.cfg'), 'w'
        ) as f:
            f.writelines(infile)

        self.test_config._merge_includes()
        nose.tools.ok_(
            'test_statistics' in self.test_config.config.keys()
        )

