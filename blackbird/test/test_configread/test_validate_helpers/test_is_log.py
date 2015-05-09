# -*- coding: utf-8 -*-

import os
import tempfile
import validate

import nose.tools

import blackbird.utils.configread


class TestConfigReaderIsLog(object):

    def __init__(self):
        self.default_logfile_name = 'blackbird.log'

    def test_exist_file(self):
        nose.tools.eq_(
            blackbird.utils.configread.is_log(__file__),
            __file__
        )

    def test_exist_dir(self):
        value = os.path.dirname(__file__)
        nose.tools.eq_(
            blackbird.utils.configread.is_log(value),
            os.path.join(value, self.default_logfile_name)
        )

    @nose.tools.raises(validate.VdtValueError)
    def test_cannot_write_file(self):
        value = tempfile.NamedTemporaryFile(mode='r', dir=os.path.dirname(__file__))
        os.chmod(value.name, 0o444)
        blackbird.utils.configread.is_log(value.name)

    @nose.tools.raises(validate.VdtValueError)
    def test_non_exist_dir(self):
        blackbird.utils.configread.is_log('/hogehoge')

    @nose.tools.raises(validate.VdtValueError)
    def test_non_exist_both(self):
        blackbird.utils.configread.is_log('/hogehoge/hogehoge.log')

    @nose.tools.raises(validate.VdtTypeError)
    def test_file_under_file(self):
        blackbird.utils.configread.is_log(
            os.path.join(__file__, self.default_logfile_name)
        )

    def test_syslog(self):
        nose.tools.eq_(
            'syslog',
            blackbird.utils.configread.is_log('syslog')
        )


class TestConfigReaderIsLogCaseOfCreatingDirectory(object):

    def __init__(self):
        self.cannot_write_dir = os.path.join(
            os.path.dirname(__file__),
            'cannot_write_dir'
        )

    def setup(self):
        os.mkdir(self.cannot_write_dir, 0o000)

    def teardown(self):
        os.rmdir(self.cannot_write_dir)

    @nose.tools.raises(validate.VdtValueError)
    def test_cannot_write_dir(self):
        blackbird.utils.configread.is_log(self.cannot_write_dir)

