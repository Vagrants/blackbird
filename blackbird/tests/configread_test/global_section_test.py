# -*- coding: utf-8 -*-
"""
Test suite for global section in configread module.
"""
import os
import lockfile
import tempfile
import validate

from nose.tools import eq_, ok_, raises

from blackbird.tests.configread_test.base import ConfigReaderBase
from blackbird.utils import configread
from blackbird.utils.configread import ConfigReader


class TestIncludeDir(ConfigReaderBase):

    def read_include_exists_test(self):
        """
        ConfigReader._read_include() read the files exists.

        Create include file named conf.d/NamedTemporaryFile.cfg,
        and read the this file, add this file's information config obj.
        """
        cfg_lines = (
            '[global]',
            'include = {0}/conf.d/*.cfg'.format(self.tmp_dir),
        )
        include_lines = (
            '[local_memcached]\n'
            'module = memcached'
        )
        os.mkdir('{0}/conf.d'.format(self.tmp_dir))
        include_file = tempfile.NamedTemporaryFile(
            suffix='.cfg',
            dir='{0}/conf.d'.format(self.tmp_dir),
        )
        include_file.write(include_lines)
        include_file.seek(0)

        config = ConfigReader(infile=cfg_lines).config
        include_file.close()
        ok_('local_memcached' in config,
            msg='All config value: {0}'.format(config))

    def read_include_no_match_glob_test(self):
        """
        ConfigReader._read_include() specify include but no match glob files.
        """
        cfg_lines = (
            '[global]',
            'include = {0}/conf.d/*.cfg'.format(self.tmp_dir),
        )
        include_lines = (
            '[local_memcached]\n'
            'module = memcached'
        )
        os.mkdir('{0}/conf.d'.format(self.tmp_dir))
        include_file = tempfile.NamedTemporaryFile(
            suffix='.conf',
            dir='{0}/conf.d'.format(self.tmp_dir),
        )
        include_file.write(include_lines)
        include_file.seek(0)

        config = ConfigReader(infile=cfg_lines).config
        include_file.close()
        eq_('local_memcached' in config, False,
            msg='Wrong config files are read.')


class TestSetModuleDir(ConfigReaderBase):
    """
    Tests suite for ConfigReader._set_default_module_dir().
    """
    def nonset_additional_dir_test(self):
        """
        ConfigReader._set_default_module_dir() default.
        Additional dir is None.
        ConfigReader adds only './threads' to config object.
        """
        cfg_lines = (
            '[global]',
            ''
        )
        config = ConfigReader(infile=cfg_lines).config
        check_value = os.path.abspath('plugins')

        ok_(check_value in config['global']['module_dir'],
            msg=('Doesn\'t insert default "module_dir" value.'
                 'All config value: {0}'.format(config)
                 )
            )

    def set_additional_dir_test(self):
        """
        ConfigReader._set_default_module_dir() add dir.
        Additional dir parameter is exists.
        May insert default value(./threads)
        and specified value by using 'module_dir' option
        into ConfigReader.config['global']['module_dir'].
        """
        cfg_lines = (
            '[global]',
            'module_dir = {0}/tests_threads'.format(self.tmp_dir)
        )
        os.mkdir('{0}/tests_threads'.format(self.tmp_dir))

        config = ConfigReader(infile=cfg_lines).config
        check_value = '{0}/tests_threads'.format(self.tmp_dir)

        ok_(check_value in config['global']['module_dir'],
            msg=('Doesn\'t exsist additional "module_dir" value.'
                 'All config value: {0}'.format(config)
                 )
            )


class TestValidateHelpersIsDir(ConfigReaderBase):
    """
    configread.is_dir() tests. This function is helper function for validation.
    """
    def is_dir_valid_directory_test(self):
        check_value = os.path.join(self.tmp_dir, 'test_dir')
        os.mkdir(check_value)

        ok_(configread.is_dir(check_value))

    @raises(IOError)
    def is_dir_not_exists_test(self):
        check_value = os.path.join(self.tmp_dir, 'test_dir')

        ok_(configread.is_dir(check_value))

    @raises(validate.VdtTypeError)
    def is_dir_valid_file_test(self):
        tmp_file = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = os.path.join(self.tmp_dir, tmp_file.name)

        ok_(configread.is_dir(check_value))

    @raises(OSError)
    def is_dir_valid_cannot_read_test(self):
        check_value = os.path.join(self.tmp_dir, 'test_dir')
        os.mkdir(check_value, 0000)

        ok_(configread.is_dir(check_value))


class TestValidateHelpersIsPid(ConfigReaderBase):
    """
    configread.is_pid() tests. This function is helper function for validation.
    """
    def __init__(self):
        self.pid_name = 'blackbird.pid'

    def is_pid_valid_file_test(self):
        check_value = os.path.join(self.tmp_dir, self.pid_name)

        eq_(configread.is_pid(check_value), check_value)

    @raises(lockfile.AlreadyLocked)
    def is_pid_already_exists(self):
        pid_file = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = os.path.join(self.tmp_dir, pid_file.name)

        ok_(configread.is_pid(check_value))

    def is_pid_valid_dir_test(self):
        pid_dir = os.path.join(self.tmp_dir, 'pid_dir')
        os.mkdir(pid_dir)
        check_value = os.path.join(pid_dir, self.pid_name)

        eq_(configread.is_pid(pid_dir), check_value)

    @raises(OSError)
    def is_pid_cannot_write_dir_test(self):
        pid_dir = os.path.join(self.tmp_dir, 'pid_dir')
        os.mkdir(pid_dir, 0000)

        ok_(configread.is_pid(pid_dir))

    @raises(OSError)
    def is_pid_cannot_write_upper_dir_test(self):
        pid_dir = os.path.join(self.tmp_dir, 'pid_dir')
        os.mkdir(pid_dir, 0000)

        ok_(configread.is_pid(os.path.join(pid_dir, self.pid_name)))

    @raises(validate.VdtTypeError)
    def is_pid_upper_dir_is_file_test(self):
        tmp_file = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = os.path.join(self.tmp_dir, tmp_file.name, self.pid_name)

        ok_(configread.is_pid(check_value))

    @raises(IOError)
    def is_pid_upper_dir_not_exists_test(self):
        check_value = os.path.join(
            self.tmp_dir,
            'NotExistsDirectory',
            self.pid_name
        )
        ok_(configread.is_pid(check_value))


class TestValidateHelpersIsLog(ConfigReaderBase):
    """
    configread.is_log() tests.
    This function checks
    whether 'log_file' option in global section is valid value.
    """

    def __init__(self):
        self.log_name = 'blackbird.log'

    def is_log_fist_time_exec_test(self):
        """
        case specified value as following:
        /var/log/blackbird.log
        * blackbird.log does not exists.
            + This means often the first-time execution of blackbird.
        * /var/log(directory) exists.
        """
        check_value = os.path.join(self.tmp_dir, self.log_name)
        eq_(configread.is_log(check_value), check_value)

    @raises(OSError)
    def is_log_cannot_write_upper_dir_test(self):
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

    def is_log_exists_file_test(self):
        """
        case specified value as following:
        /var/log/blackbird/blackbird.log
        * specified file exists.
        * execution user has write permission.
        """
        log_file = tempfile.NamedTemporaryFile(dir=self.tmp_dir)
        check_value = log_file.name

        eq_(configread.is_log(check_value), check_value)

    @raises(OSError)
    def is_log_cannot_write_file_test(self):
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

    def is_log_exists_dir_test(self):
        """
        case specified value as following:
        /tmp
        * specified value is directory.
        * execution user has write permission.
        """
        check_value = os.path.join(self.tmp_dir, self.log_name)
        eq_(configread.is_log(check_value), check_value)

    @raises(OSError)
    def is_log_cannot_write_dir_test(self):
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
    def is_log_valid_dir_is_file_test(self):
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

    @raises(IOError)
    def is_log_valid_dir_not_exists_test(self):
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
        self.valid_username = 'root'
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


class TestValidateHelperIsUser(ConfigReaderBase):

    def __init__(self):
        self.valid_groupname = 'root'
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
