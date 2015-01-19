# -*- coding: utf-8 -*-

import logging
import logging.handlers
import sys
import platform


def logger_factory(filename, level, fmt='ltsv'):

    logger = logging.getLogger('blackbird')

    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }
    logger.setLevel(levels.get(level))

    if filename == sys.stdout:
        handler = logging.StreamHandler(filename)
    elif filename.lower() == 'syslog':
        if platform.system() == 'Darwin':
            # mac os
            address = '/var/run/syslog'
        else:
            # other linux
            address = '/dev/log'
        handler = logging.handlers.SysLogHandler(
            address=address,
            facility=logging.handlers.SysLogHandler.LOG_LOCAL6
        )
    else:
        handler = logging.handlers.WatchedFileHandler(filename, encoding='UTF-8', delay=True)

    formats = {
        'ltsv': (
            "log_level:%(levelname)s\t"
            "time:%(asctime)s\t"
            "process:%(name)s\t"
            "thread:%(threadName)s\t"
            "message:%(message)s"
        ),
        'combined': (
            "%(asctime)s "
            "[%(levelname)s] "
            "%(threadName)s "
            "%(message)s"
        ),
    }
    datefmt = "%d/%b/%Y:%H:%M:%S %z"
    format = formats.get(fmt)
    formatter = logging.Formatter(fmt=format, datefmt=datefmt)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
