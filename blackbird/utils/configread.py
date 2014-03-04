# -*- coding: utf-8 -*-
"""
Read config file(default: conf/defaults.cfg)
Default config file name is hard-corded.
"""
import configobj
import errno
import glob
import grp
import ipaddr
import os
import pkgutil
import pwd
import sys
import validate

from blackbird.utils import base as base
from blackbird.utils import helpers
from blackbird.utils import argumentparse


class JobObserver(base.Observer):
    """
    This class is Observer for registering JobObjects.
    By default, JobObject is ConcreteJob class in ./threads/*.py.
    At here, ConfigReader is subject to JobObserver.

    And this class has self.jobs as follows:
    self.jobs = {
        'redis' = <class 'threads.hoge_redis.ConcreteJob'>
        ...
    }
    """

    def __init__(self):
        self.jobs = {}

    def update(self, name, job):
        u"""
        Update self.jobs.
        This method is called by ConfigReader.notify().
        """

        self.jobs[name] = (job)


class ConfigReader(base.Subject):
    """
    ConfigObj isn't written that expect to you(and I) override.
    So, ConfigReader generate ConfigObj instance at internal.
    ConfigReader call Original function to ConfigObj instance.
    For example, _override_section(self).
    Return ConfigObj instance after called several function.
    """

    def __init__(self, infile, observers=None):
        self.config = self._configobj_factory(infile)

        #validate config file
        self._read_include()
        self.config['global'].update(self._set_default_module_dir())
        self._global_validate()
        self._validate()

        #notify observers
        self._observers = []
        self.register(observers)
        self._register_jobs()

    def _configobj_factory(self,
                           infile,
                           raise_errors=True,
                           list_values=True,
                           file_error=True,
                           interpolation=False,
                           configspec=None,
                           stringify=True,
                           _inspec=False
                           ):
        """
        Factory Method.
        Create Configobj instance and register it to self.config.
        This method also is used to create configspec instance.
        Because configspec instance also is ConfigObj instance.
        """

        return configobj.ConfigObj(infile=infile,
                                   raise_errors=raise_errors,
                                   list_values=list_values,
                                   file_error=file_error,
                                   interpolation=interpolation,
                                   configspec=configspec,
                                   stringify=stringify,
                                   _inspec=_inspec
                                   )

    def _set_include(self):
        """
        self.config['global']['include']
        must be relative path from "conf/defaults.cfg"
        or absolute path.
        This method returns value after converting to absolute path.
        And this function validate self.config['global']['include'].
        Check whether File path that is specified by include option exists.
        Specially, include option is validated by ConfigReader._set_include().

        This method is called by ConfigReader._read_include().
        """

        # If include option is relative path, convert absolute path.
        if not os.path.isabs(self.config['global']['include']):
            include = self.config['global']['include']
            default = os.path.dirname(os.path.abspath(self.config.filename))
            self.config['global']['include'] = os.path.join(default,
                                                            include
                                                            )

        if os.path.isdir(self.config['global']['include']):
            directory = self.config['global']['include']
            self.config['global']['include'] = os.path.join(directory, '*')
        else:
            directory = os.path.split(self.config['global']['include'])[0]

        if os.path.exists(directory):
            if not os.access(directory, os.R_OK):
                err_message = ('{directory}: Permission denied.'
                               ''.format(directory=directory)
                               )
                raise OSError(errno.EACCES, err_message)

        else:
            err_message = ('{directory}: No such file or directory.'
                           ''.format(directory=directory)
                           )
            raise IOError(errno.ENOENT, err_message)

    def _read_include(self):
        """
        If "include" option exists in "default.cfg",
        read the file(glob-match) in the directory.
        """
        if 'include' in self.config['global']:
            self._set_include()

            include_files = glob.glob(self.config['global']['include'])

            for infile in include_files:
                cfg = self._configobj_factory(infile=infile)
                self.config.merge(cfg)

    def register(self, observers):
        u"""
        Concrete method of Subject.register().
        Register observers as an argument to self.observers.
        """

        if isinstance(observers, list) or isinstance(observers, tuple):

            for observer in observers:
                # check whether inhelitance "base.Observer"
                if isinstance(observer, base.Observer):
                    self._observers.append(observer)

                else:
                    raise InhelitanceError(base.Observer.__name__)

        elif isinstance(observers, base.Observer):
            self._observers.append(observers)

    def unregister(self, observers):
        u"""
        Concrete method of Subject.unregister().
        Unregister observers as an argument to self.observers.
        """

        if isinstance(observers, list) or isinstance(observers, tuple):
            for observer in observers:
                try:
                    index = self._observers.index(observer)
                    self._observers.remove(self._observers[index])
                except ValueError:
                    # logging
                    print('{observer} not in list...'.format(observer))

        elif isinstance(observers, base.Observer):
            try:
                index = self._observers.index(observers)
                self._observers.remove(self._observers[index])
            except ValueError:
                # logging
                print('{observer} not in list...'.format(observer))

        else:
            err_message = ('ConfigReader.register support'
                           'ListType, TupleType and {observer} Object.'
                           ''.format(base.Observer.__name__)
                           )

            raise ValueError(err_message)

    def notify(self, name, job):
        """
        Concrete method of Subject.notify().
        Notify to change the status of Subject for observer.
        This method call Observer.update().
        In this program, ConfigReader.notify() call JobObserver.update().
        For exmaple, register threads.redis.ConcreateJob to JobObserver.jobs.
        """
        for observer in self._observers:
            observer.update(name, job)

    def _set_default_module_dir(self):
        """
        Default "module_dir" is "./plugins" and "/opt/blackbird/plugins".
        "./plugins" is relative path from ./sr71.py.
        "module_dir" is used in _get_modules().
        Plugins under the "module_dir" is written about each job.
        """

        default_module_dir1 = './plugins'
        default_module_dir2 = '/opt/blackbird/plugins'

        if not os.path.exists('./plugins'):
            default_module_dir1 = os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'plugins',
            )

        if 'module_dir' in self.config['global']:
            default_module_dir2 = self.config['global']['module_dir']

        module_dirs = [default_module_dir1, default_module_dir2]
        option = {'module_dir': module_dirs}
        return option

    def _global_validate(self):
        """
        Validate only global section.
        The options in global section
        is used by other private methods of ConfigReader.
        So, validate only global section at first.
        "raw_spec" is configspec for global section.
        "functions" is passed as an argument in "validate.Validator".

        about "functions"
            'name': <function object>
             'name':used in configspec.
             Same meaning as "string", "integer" and "float" in validate.py.
             <function object>: function which is determine by the 'name'.

        e.g: the contents of ConfigSpec File
            [hoge]
            ham = egg(default=fuga)

        Functions
            functions = {
                'egg': is_egg
            }

        When validation, 'is_egg' function is called for ham option.
        """

        raw_spec = (
            "[global]",
            "user = user(default=bbd)",
            "group = group(default=bbd)",
            "log_file = log(default=/var/log/blackbird/blackbird.log)",
            "log_level = log_level(default='warn')",
            "max_queue_length = integer(default=32767)",
            "lld_interval = integer(default=600)",
            "interval = integer(default=10)"
        )

        functions = {
            'user': is_user,
            'group': is_group,
            'dir': extend_is_dir,
            'log': is_log,
            'log_level': is_log_level
        }

        validator = validate.Validator(functions=functions)
        spec = self._configobj_factory(infile=raw_spec,
                                       _inspec=True
                                       )
        self.config.configspec = spec
        result = self.config.validate(validator, preserve_errors=True)
        self._parse_result(result)

        self.config['global'].configspec = None

    def _get_modules(self):
        """
        Get modules under the self.config['global']['module_dirs'] directories.
        Plugin modules has the two classes of "ConcreteJob" and "Validator".
        Further, "Validator.module" property is used to
        deciding which one to use plugin module.

        This method returns a dictionary as following:
        modules = {
            'redis': <module 'MODULE_NAME' from 'REAL_FILE_NAME'>,
            'memcached': <module 'MODULE_NAME' from 'REAL_FILE_NAME'>
            ...
        }

        At here,
        collect all plugin modules under the self._module_dirs directories.
        Plugins that were collected by this method is used
        in ConfigReader._register_jobs() and ConfigReader._get_raw_specs().
        """

        not_import = set()
        not_import.add('base')
        modules = {}

        for path in self.config['global']['module_dir']:
            sys.path.insert(0, path)
            iter_modules = pkgutil.iter_modules([path])

            for module_info in iter_modules:
                module_name = module_info[1]

                if module_name in not_import:
                    continue

                if helpers.helper_import(module_name, 'Validator'):
                    module = helpers.helper_import(module_name)
                    modules[module.__name__] = module

            sys.path.remove(path)

        return modules

    def _register_jobs(self):
        """
        This method extracts only the "ConcreteJob" class
        from modules that were collected by ConfigReader._get_modules().
        And, this method called Subject.notify(),
        append "ConcreteJob" classes to JobObserver.jobs.
        """

        #job_name is hard-corded
        job_name = 'ConcreteJob'
        modules = self._get_modules()

        for section, options in self.config.items():

            if section == 'global':
                continue

            try:
                name = options['module']
            except KeyError:
                raise ConfigMissingValue(section, 'module')

            try:
                job = getattr(modules[name], job_name)
                self.notify(name, job)
            except KeyError:
                raise NotSupportedError(name)

    def _get_raw_specs(self, config):
        """
        This method extract only the "Validate.spec" from
        modules that were collected by ConfigReader._get_modules().
        And, this method append "Validate.spec" to raw_specs.
        This method creates a dictionary like the following:
        raw_specs = {
            'redis': (
                "[redis]",
                "host = ipaddress(default='127.0.0.1')",
                "port = integer(0, 65535, default=6379)",
                "db = integer(default=0)",
                "charset = string(default='utf-8')",
                "password = string(default=None)"
            ),
            ...
        }

        raw_specs is used by ConfigReader._create_specs().
        """

        #spec_name is hard-corded
        raw_specs = {}
        spec_name = 'Validator'
        modules = self._get_modules()

        for section, options in config.items():

            if section == 'global':
                continue

            try:
                name = options['module']
            except KeyError:
                raise ConfigMissingValue(section, 'module')

            try:
                spec = getattr(modules[name], spec_name)().spec
                raw_specs[name] = spec
            except KeyError:
                raise NotSupportedError(name)

        return raw_specs

    def _create_specs(self):
        """
        Create configspec instances based "conf/defaults.cfg".
        This function takes as arguments to the required section and module.
        Take them out from self.config, _create_specs pass the _config_factory.
        """

        raw_specs = self._get_raw_specs(self.config)
        spec = self._configobj_factory(infile=None,
                                       _inspec=True
                                       )

        for section, options in self.config.items():

            if section == 'global':
                continue

            if 'module' in options:
                module = options['module']
            else:
                raise ConfigMissingValue(section, 'module')

            spec.merge(self._configspec_factory(section=section,
                                                module=module,
                                                infile=raw_specs[module]
                                                )
                       )

        return spec

    def _configspec_factory(self, section, module, infile):
        """
        ConfigObj(_inspec=True) factory method.
        ConfibObj instance that the "_inspec" argument is True
        is called "configspec".

        This method is called by ConfigReader._create_specs().
        Beforehand, you need to define
        type definitions and default values in "spec file" as follow:
        [memcached]
        module = string('memcached')
        host = ipaddr(default='127.0.0.1')
        port = integer(0, 65535, default=11211)

        Notes: Must be the same all The following values.
            "module" as the argument of _configspec_factory()
            "module" in the spec file
            section name in the spec file
                (e.g: section name is [memcached] in the above case.)

        This method load the modules under the directories
        that is specified in config['global']['module_dir'] option,
        and return converted "configspec" for conf/defaults.cfg.

        Returned configspec is as follows:
        [local_memcached]
        module = string('memcached')
        host = ipaddr(default='127.0.0.1')
        port = integer(0, 65535, default=11211)

        In short Rename section name in spec file
        from [memcached] to specified [local_memcached] in conf/defaults.cfg.
        """

        configspec = self._configobj_factory(infile=infile,
                                             #file_error=False,
                                             _inspec=True
                                             )

        #Override the name of section in spec file by given module as argument.
        configspec.rename(module, section)

        return configspec

    def _validate(self):
        """
        validate whether value in config file is correct.
        """

        spec = self._create_specs()
        functions = {
            'ipaddress': is_ipaddress,
        }
        validator = validate.Validator(functions=functions)

        self.config.configspec = spec
        result = self.config.validate(validator, preserve_errors=True)

        if self._parse_result(result):
            return True

    def _parse_result(self, result):
        u"""
        This method parses validation results.
        If result is True, then do nothing.
        if include even one false to result,
        this method parse result and raise Exception.
        """
        if result is not True:
            for section, errors in result.iteritems():
                for key, value in errors.iteritems():
                    if value is not True:
                        message = (
                            '"{0}" option in [{1}] is invalid value. {2}'
                            ''.format(key, section, value)
                        )
                        print(message)

            err_message = (
                'Some options are invalid!!! Please see the log!!!'
            )
            raise validate.ValidateError(err_message)

        else:
            return True


class ConfigMissingValue(ValueError):
    u"""
    Raise this error, when specified section does not have the key.
    Take section and key as arguments.
    """

    def __init__(self, section, key):
        u"""Error when key doesn't exist in the particular section."""
        err_message = ('"{key}" option doesn\'t exist in "{section}" section'
                       ''.format(key=key, section=section))

        super(ConfigMissingValue, self).__init__(err_message)


class InhelitanceError(ValueError):
    u"""
    Raise this error, when one class inhelit from a parent class.
    """

    def __init__(self, class_name):
        err_message = ('doesn\'t inhelit from a {class_name}'
                       ''.format(class_name=class_name)
                       )

        super(InhelitanceError, self).__init__(err_message)


class NotSupportedError(ValueError):
    u"""
    Raise this error, when specify module that not exists
    at "module" option in config file.
    """

    def __init__(self, module):
        err_message = ('Sorry! Not supported \'{module}\'...'
                       ''.format(module=module)
                       )

        super(NotSupportedError, self).__init__(err_message)


def is_ipaddress(value):
    u"""
    Check whether correct IPAdress.
    This function is defferent with built-in "ip_addr"-type.
    Built-in "ip_addr"-type only supports IPv4.
    But, "ipaddr" (google products) supports both IPv4 and IPv6.
    This function's name is not like "return_ipaddress", but "is_ipaddress"
    because it's called by ConfigReader._validate().
    Names of functions by used in _validate() must be "is_TYPE".
    """

    try:
        ipaddress = ipaddr.IPAddress(value)
    except ValueError:
        raise validate.VdtValueError(value)

    return ipaddress.exploded


def is_dir(value):
    """
    This function checks whether given path as argument exists,
    and whether direcoty.
    """

    value = os.path.expanduser(value)
    value = os.path.expandvars(value)
    value = os.path.abspath(value)

    if os.path.exists(value):
        if os.path.isdir(value):
            if os.access(value, os.R_OK):
                return value

            else:
                err_message = ('{path}: Permission denied.'
                               ''.format(path=value)
                               )
                raise validate.VdtValueError(err_message)
        else:
            err_message = ('{value} is file.'
                           ''.format(value=value)
                           )
            raise validate.VdtTypeError(err_message)
    else:
        err_message = ('{path}: No such file or directory.'
                       ''.format(path=value)
                       )
        raise validate.VdtValueError(err_message)


def extend_is_dir(value, minimum=None, maximum=None):
    u"""
    This function is extended is_dir().
    This function was able to take ListType or StringType as argument.
    """

    if isinstance(value, list):
        return [is_dir(member)
                for member in validate.is_list(value, minimum, maximum)]

    else:
        return is_dir(value)


def is_log(value):
    """
    This function checks whether file path
    that is specified at "log_file" option eixsts,
    whether write permission to the file path.

    Return the following value:
    case1: exists path and write permission
        is_log('/tmp')
            '/tmp/hogehoge.log'

    case2: non-exists path and write permission
        is_log('/tmp/hogehoge')
            '/tmp/hogehoge'
        In this case, 'hogehoge' doesn't exist.
        but 'hogehoge' is considered as a file.
        Thus, create log file named 'hogehoge'.

    case3: complete non-exists path
        is_pid('/tmp/hogehoge/fugafuga')
            IOError: [Error 2] No such file or directory.
        The last part of given path is only considered log_file's name.
        In this case, "fugafuga" is considered log_file's name.

    In any case, check whether given path exists before checking permission.

    Notes: Even if given relative path, works fine.
           But, if don't use as much as possible if good.

           Recommended giving he full path including the file name.
    """

    value = os.path.expanduser(value)
    value = os.path.expandvars(value)
    value = os.path.abspath(value)

    log_file = 'blackbird.log'

    if os.path.exists(value):

        if os.path.isdir(value):

            if os.access(value, os.W_OK):
                return os.path.join(value, log_file)

            else:
                err_message = ('{path}: Permission denied.'
                               ''.format(path=value)
                               )
                raise validate.VdtValueError(err_message)

        else:

            if os.access(value, os.W_OK):
                return value

            else:
                err_message = ('{path}: Permission denied.'
                               ''.format(path=value)
                               )
                raise validate.VdtValueError(err_message)

    else:
        directory = os.path.split(value)[0]
        log_file = os.path.split(value)[0]

        if os.path.isdir(directory):

            if os.access(directory, os.W_OK):
                return value

            else:
                err_message = ('{directory}: Permission denied.'
                               ''.format(directory=directory)
                               )
                raise validate.VdtValueError(err_message)

        else:

            if os.path.exists(directory):
                err_message = ('{directory} is file.'
                               ''.format(directory=directory)
                               )
                raise validate.VdtTypeError(err_message)

            else:
                err_message = ('{directory}: No such file or directory.'
                               ''.format(directory=directory)
                               )
                raise validate.VdtValueError(err_message)


def is_log_level(value):
    u"""
    Check whether the value as argument be included the following list.
    ['debug', 'info', 'warn', 'error', 'crit']
    """

    log_levels = ['debug', 'info', 'warn', 'error', 'crit']

    if value in log_levels:
        return value

    else:
        err_message = ('"log_level" supported following value: '
                       '{0}'.format(log_levels)
                       )
        raise validate.VdtValueError(err_message)


def is_user(value, min=None, max=None):
    """
    Check whether username or uid as argument exists.
    if this function recieved username, convert uid and exec validation.
    """

    if type(value) == str:
        try:
            entry = pwd.getpwnam(value)
            value = entry.pw_uid
        except KeyError:
            err_message = ('{0}: No such user.'.format(value))
            raise validate.VdtValueError(err_message)

        return value

    elif type(value) == int:
        try:
            pwd.getpwuid(value)
        except KeyError:
            err_message = ('{0}: No such user.'.format(value))
            raise validate.VdtValueError(err_message)

        return value

    else:
        err_message = ('Please, use str or int to "user" parameter.')
        raise validate.VdtTypeError(err_message)


def is_group(value):
    """
    Check whether groupname or gid as argument exists.
    if this function recieved groupname, convert gid and exec validation.
    """

    if type(value) == str:
        try:
            entry = grp.getgrnam(value)
            value = entry.gr_gid
        except KeyError:
            err_message = ('{0}: No such group.'.format(value))
            raise validate.VdtValueError(err_message)

        return value

    elif type(value) == int:
        try:
            grp.getgrgid(value)
        except KeyError:
            err_message = ('{0}: No such group.'.format(value))
            raise validate.VdtValueError(err_message)

        return value

    else:
        err_message = ('Please, use str or int to "user" parameter.')
        raise validate.VdtTypeError(err_message)
