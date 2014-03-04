# -*- coding:utf-8 -*-

import argparse
import os

import validate


def get_args():
    u"""
    ./main --config /etc/blackbird/etc/default.cfg --debug ...
    Return command-line options(arguments).
    """

    description = "The Daemon send various value for zabbix_sender."
    parser = argparse.ArgumentParser(description)

    parser.add_argument('--config', '-c',
                        default='conf/defaults.cfg',
                        help='Specify "defaults.cfg" file'
                        )

    parser.add_argument('--debug-mode', '-d',
                        action='store_true',
                        help='Turn on debug mode',
                        dest='debug_mode'
                        )

    parser.add_argument('--pid-file', '-p',
                        default=os.path.join(
                            os.path.abspath(os.path.curdir),
                            'blackbird.pid'
                        ),
                        help='pid file location',
                        dest='pid_file'
                        )

    args = parser.parse_args()
    args.pid_file = is_pid(args.pid_file)

    return parser.parse_args()


def is_pid(value):
    """
    This function checks whether file path
    that is specified at "pid_file" option eixsts,
    whether write permission to the file path.

    Return the following value:
    case1: exists path and write permission
        is_pid('/tmp')
            '/tmp/hogehoge.pid'

    case2: non-exists path and write permission
        is_pid('/tmp/hogehoge')
            '/tmp/hogehoge'
        In this case, hogehoge doesn't exist.
        but hogehoge is considered as a file.
        Thus, create pid file named 'hogehoge'.

    case3: complete non-exists path
        is_pid('/tmp/hogehoge/fugafuga')
            IOError: [Error 2] No such file or directory.
        The last part of given path is only considered pid_file's name.
        In this case, "fugafuga" is considered pid_file's name.

    In any case, check whether given path exists before checking permission.

    Notes: Even if given relative path, works fine.
           But, if don't use as much as possible if good.

           Recommended giving the absolute path including the pid file name.
    """

    value = os.path.expanduser(value)
    value = os.path.expandvars(value)
    value = os.path.abspath(value)

    pid_file = 'blackbird.pid'

    if os.path.exists(value):

        if os.path.isdir(value):

            if os.access(value, os.W_OK):
                return os.path.join(value, pid_file)

            else:
                err_message = ('{path}: Permission denied.'
                               ''.format(path=value)
                               )
                raise validate.VdtValueError(err_message)

        else:
            err_message = 'pid file already exists.'
            raise lockfile.AlreadyLocked(err_message)

    else:
        directory = os.path.split(value)[0]

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
