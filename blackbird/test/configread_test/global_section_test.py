# -*- coding: utf-8 -*-
"""
Test suite for global section in configread module.
"""
import os
import lockfile
import tempfile
import validate

from nose.tools import eq_, ok_, raises

from blackbird.test.configread_test.base import ConfigReaderBase
from blackbird.utils import configread
from blackbird.utils import argumentparse


class TestValidateHelpersIsPid(ConfigReaderBase):
    def __init__(self):
        self.pid_name = 'blackbird.pid'

    def test_valid_file(self):
        check_value = os.path.join(self.tmp_dir, self.pid_name)

        eq_(argumentparse.is_pid(check_value), check_value)

    @raises(lockfile.AlreadyLocked)
    def test_already_exists(self):
        pid_file = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = os.path.join(self.tmp_dir, pid_file.name)

        ok_(argumentparse.is_pid(check_value))

    def test_exist_dir(self):
        dirname = os.path.dirname(__file__)
        eq_(
            argumentparse.is_pid(dirname),
            os.path.join(
                dirname, self.pid_name
            )
        )

    @raises(validate.VdtValueError)
    def test_cannot_write_dir(self):
        pid_dir = os.path.join(self.tmp_dir, 'pid_dir')
        os.mkdir(pid_dir, 0000)

        ok_(argumentparse.is_pid(pid_dir))

    @raises(validate.VdtValueError)
    def test_cannot_write_upper_dir(self):
        pid_dir = os.path.join(self.tmp_dir, 'pid_dir')
        os.mkdir(pid_dir, 0000)

        ok_(argumentparse.is_pid(os.path.join(pid_dir, self.pid_name)))

    @raises(validate.VdtTypeError)
    def test_assume_file_to_directory(self):
        ok_(
            argumentparse.is_pid(
                os.path.join(__file__, self.pid_name)
            )
        )

    @raises(validate.VdtValueError)
    def is_pid_upper_dir_not_exists_test(self):
        ok_(
            argumentparse.is_pid(
                os.path.join('/hogehoge', self.pid_name)
            )
        )


class TestValidateHelperIsUser(ConfigReaderBase):

    def __init__(self):
        self.valid_username = 'nobody'
        self.valid_uid = 0
        self.invalid_username = 'hogehoge'
        self.invalid_uid = 655355

    def exists_username_test(self):
        ok_(type(configread.is_user(self.valid_username)) == int)

    @raises(validate.VdtValueError)
    def not_exists_username_test(self):
        configread.is_user(self.invalid_username)

    def exists_uid_test(self):
        eq_(self.valid_uid, configread.is_user(self.valid_uid))

    @raises(validate.VdtValueError)
    def not_exists_uid_test(self):
        configread.is_user(self.invalid_uid)


class TestValidateHelperIsGroup(ConfigReaderBase):

    def __init__(self):
        self.valid_groupname = 'nobody'
        self.valid_gid = 0
        self.invalid_groupname = 'hogehoge'
        self.invalid_gid = 655355

    def exists_groupname_test(self):
        ok_(type(configread.is_group(self.valid_groupname)) == int)

    @raises(validate.VdtValueError)
    def not_exists_groupname_test(self):
        configread.is_group(self.invalid_groupname)

    def exists_gid_test(self):
        eq_(self.valid_gid, configread.is_group(self.valid_gid))

    @raises(validate.VdtValueError)
    def not_exists_gid_test(self):
        configread.is_group(self.invalid_gid)
