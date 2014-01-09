#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""main process."""

import Queue
import sys
import threading
import time
from daemon import DaemonContext

from blackbird.utils import argumentparse
from blackbird.utils import configread
from blackbird.utils import logger
from blackbird.plugins.base import BlackbirdPluginError

try:
    # for python-daemon 1.5.x(lockfile 0.8.x)
    from daemon import pidlockfile as pidlockfile
except ImportError:
    from lockfile import pidlockfile as pidlockfile


ARGS = argumentparse.get_args()
JOBS = configread.JobObserver()
CONFIG = configread.ConfigReader(ARGS.config, JOBS).config


class BlackBird(object):
    """
    BlackBird is main process.
    'utils/configread' module parses and read config file,
    collects job that is written in config file.
    """

    def __init__(self):
        self.config = CONFIG
        self.logger = self._set_logger()
        self.queue = Queue.Queue()
        self.jobs = None

        self._create_threads()

    def _set_logger(self):
        if ARGS.debug_mode:
            logger_obj = logger.logger_factory(
                sys.stdout,
                'debug'
            )
        else:
            logger_obj = logger.logger_factory(
                self.config['global']['log_file'],
                self.config['global']['log_level']
            )
        return logger_obj

    def _create_threads(self):
        """
        This method creates job instances.
        """

        creator = JobCreator(self.config, JOBS.jobs, self.queue, self.logger)
        self.jobs = creator.job_factory()

    def start(self):
        """
        main loop.
        """

        def main_loop():
            while True:
                threadnames = [thread.name for thread in threading.enumerate()]
                for job_name, concrete_job in self.jobs.items():
                    if not job_name in threadnames:
                        new_thread = Executor(
                            name=job_name,
                            job=concrete_job['method'],
                            logger=self.logger,
                            interval=concrete_job['interval']
                        )
                        new_thread.start()
                        new_thread.join(1)
                    else:
                        thread.join(1)

        if not ARGS.debug_mode:
            log_file = open(self.config['global']['log_file'], 'a+', 0)
            self.logger.info('started main process')
            pid_file = pidlockfile.PIDLockFile(ARGS.pid_file)
            with DaemonContext(
                files_preserve=[
                    self.logger.handlers[0].stream
                ],
                uid=self.config['global']['user'],
                gid=self.config['global']['group'],
                stdout=log_file,
                stderr=log_file,
                pidfile=pid_file
            ):
                main_loop()

        else:
            self.logger.info('started main process')
            main_loop()


class JobCreator(object):
    """
    JobFactory class.
    This class creates job instance from job class(ConcreteJob).
    """

    def __init__(self, config, plugins, queue, logger):
        self.config = config
        self.plugins = plugins
        self.queue = queue
        self.logger = logger

    def job_factory(self):
        """
        Create concrete jobs. The concrete jobs is following dictionary.
        jobs = {
            'PLUGINNAME-build_items': {
                'method': FUNCTION_OBJECT,
                'interval': INTERVAL_TIME ,
            }
            ...
        }
        If ConcreteJob instance has "build_discovery_items",
        "build_discovery_items" method is added to jobs.

        warn: looped method is deprecated in 0.4.0.
        You should implemente "build_items" instead of "looped_method".
        In most cases you need only to change the method name.
        """

        jobs = dict()

        for section, options in self.config.items():

            if section == 'global':
                continue

            #Since validate in utils/configread, does not occur here Error
            #In the other sections are global,
            #that there is a "module" option is collateral.
            plugin_name = options['module']
            job_kls = self.plugins[plugin_name]
            job_obj = job_kls(options, self.queue, self.logger)

            # Deprecated!!
            if hasattr(job_obj, 'looped_method'):
                self.logger.warn(
                    ('{0}\'s "looped_method" is deprecated.'
                     'Pleases change method name to "build_items"'
                     ''.format(plugin_name))
                )
                name = '-'.join([plugin_name, 'looped_method'])
                interval = 10
                if 'interval' in options:
                    interval = options['interval']

                jobs[name] = {
                    'method': job_obj.looped_method,
                    'interval': interval,
                }

            if hasattr(job_obj, 'build_items'):
                name = '-'.join([plugin_name, 'build_items'])
                interval = 60
                if 'interval' in options:
                    interval = options['interval']

                jobs[name] = {
                    'method': job_obj.build_items,
                    'interval': interval,
                }

            if hasattr(job_obj, 'build_discovery_items'):
                name = '-'.join([plugin_name, 'build_discovery_items'])
                lld_interval = 600
                if 'lld_interval' in self.config['global']:
                    lld_interval = self.config['global']['lld_interval']

                jobs[name] = {
                    'method': job_obj.build_discovery_items,
                    'interval': lld_interval,
                }

        return jobs


class Executor(threading.Thread):
    """
    job executor class.
    "interval" argument is interval of getting data.

    If you write "interval" option as following at each section in config file:
        interval = 30

    Executor get the data every 30 seconds.
    """
    def __init__(self, name, job, logger, interval):
        threading.Thread.__init__(self, name=name)
        self.setDaemon(True)
        self.job = job
        self.logger = logger
        if type(interval) is not float:
            self.interval = float(interval)
        else:
            self.interval = interval

    def run(self):
        while True:
            time.sleep(self.interval)

            try:
                self.job()
            except BlackbirdPluginError as error:
                self.logger.error(error)
                exit(1)


def main():
    sr71 = BlackBird()
    sr71.start()


if __name__ == '__main__':
    main()
