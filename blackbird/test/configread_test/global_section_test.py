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


class TestValidateHelpersIsLog(ConfigReaderBase):
    """
    Test suite of blackbird.utils.configread.is_log
    """

    def __init__(self):
        self.log_name = 'blackbird.log'

    def test_non_exist_file(self):
        """
        case specified value as following:
        /var/log/blackbird.log
        * blackbird.log does not exists.
            + This means often the first-time execution of blackbird.
        * /var/log(directory) exists.
        """
        value = os.path.join(os.path.dirname(__file__), self.log_name)
        eq_(
            configread.is_log(value), value
        )

    @raises(validate.VdtValueError)
    def test_cannot_write_upper_dir(self):
        """
        case specified value as following:
        /root/blackbird.log
        * blackbird.log does not exists.
        * /root exists
            + But, execution user doesn't have write permission.
        """
        log_dir = os.path.join(self.tmp_dir, 'CannotReadDirectory')
        os.mkdir(log_dir, 0000)
        check_value = os.path.join(log_dir, self.log_name)

        ok_(configread.is_log(check_value))

    def test_exist_file(self):
        """
        case specified value as following:
        /var/log/blackbird/blackbird.log
        * specified file exists.
        * execution user has write permission.
        """
        log_file = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = log_file.name
        eq_(configread.is_log(check_value), check_value)

    @raises(validate.VdtValueError)
    def test_cannot_write_file(self):
        """
        case specified value as following:
        /var/log/messages
        * specified file exists.
        * execution doesn't have write permission.
        """
        log_file = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = log_file.name
        os.chmod(check_value, 0000)
        ok_(configread.is_log(check_value))

    def test_exist_dir(self):
        """
        case specified value as following:
        /tmp
        * specified value is directory.
        * execution user has write permission.
        """
        check_value = os.path.dirname(__file__)
        eq_(
            configread.is_log(check_value),
            os.path.join(check_value, self.log_name)
        )

    @raises(validate.VdtValueError)
    def test_cannot_write_dir(self):
        """
        case specified value as following:
        /var/log
        * specified value is directory.
        * execution user does not have write permission.
        """
        log_dir = os.path.join(self.tmp_dir, 'CannotReadDirectory')
        os.mkdir(log_dir, 0000)

        ok_(configread.is_log(log_dir))

    @raises(validate.VdtTypeError)
    def test_assume_file_to_dir(self):
        """
        case specified value as following:
        /var/log/messages/blackbird.log
        * /var/log/messages exists.
        * But, /var/log/messages is the file.
            + This means following...
                - If specified value does not exists, check upper directory.
        """
        log_dir = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = os.path.join(log_dir.name, self.log_name)
        ok_(configread.is_log(check_value))

    @raises(validate.VdtValueError)
    def test_non_exist_dir_with_file(self):
        """
        case specified value as following:
        /blackbird/blackbird.log
        * /blackbird/blackbird.log does not exists.
        * /blackbird does not exists, too.
        """
        check_value = os.path.join(
            self.tmp_dir,
            'NotExistsDirectory',
            self.log_name
        )
        ok_(configread.is_log(check_value))


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
