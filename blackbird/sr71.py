# -*- coding:utf-8 -*-
"""main process."""

import Queue
import inspect
import os
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


class BlackBird(object):
    """
    BlackBird is main process.
    'blackbird/utils/configread.py' module
    parses and read config file,
    collects job that is written in config file.
    """

    def __init__(self):
        self.args = argumentparse.get_args()

        self.observers = configread.JobObserver()
        self.config = configread.ConfigReader(
            self.args.config, self.observers
        ).config
        self.logger = self._set_logger()

        self.jobs = None

        self._add_arguments(self.args)
        self._create_threads()

    def _set_logger(self):
        if self.args.debug_mode:
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

    def _add_arguments(self, args):
        """
        Add command line arguments to each section in config.
        e.x:
        before:
            [global]
            hoge = hoge

        after:
            {
                'global': {
                    'hoge': 'hoge',
                    'arguments': {
                        'debug_mode': True,
                        'and_more': AND_MORE
                    }
                }
            }
        """
        update_dict = {
            'arguments': vars(args)
        }
        for section in self.config.keys():
            self.config[section].update(update_dict)

    def _create_threads(self):
        """
        This method creates job instances.
        """

        creator = JobCreator(
            self.config,
            self.observers.jobs,
            self.logger
        )
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

        if not self.args.debug_mode:
            log_file = open(self.config['global']['log_file'], 'a+', 0)
            log_file_stat = os.lstat(self.config['global']['log_file'])

            if log_file_stat.st_uid != self.config['global']['user']:
                os.chown(self.config['global']['log_file'],
                         self.config['global']['user'],
                         -1
                         )
            if log_file_stat.st_gid != self.config['global']['group']:
                os.chown(self.config['global']['log_file'],
                         -1,
                         self.config['global']['group']
                         )

            self.logger.info('started main process')
            pid_file = pidlockfile.PIDLockFile(self.args.pid_file)
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

    def __init__(self, config, plugins, logger):
        self.config = config
        self.plugins = plugins
        self.queue = Queue.Queue(
            config['global']['max_queue_length']
        )
        self.stats_queue = Queue.Queue(
            config['global']['max_queue_length']
        )
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

            if hasattr(job_kls, '__init__'):
                job_argspec = inspect.getargspec(job_kls.__init__)

                if 'stats_queue' in job_argspec.args:
                    job_obj = job_kls(
                        options=options,
                        queue=self.queue,
                        stats_queue=self.stats_queue,
                        logger=self.logger
                    )

                else:
                    job_obj = job_kls(
                        options=options,
                        queue=self.queue,
                        logger=self.logger
                    )

            # Deprecated!!
            if hasattr(job_obj, 'looped_method'):
                self.logger.warn(
                    ('{0}\'s "looped_method" is deprecated.'
                     'Pleases change method name to "build_items"'
                     ''.format(plugin_name))
                )
                name = '-'.join([section, 'looped_method'])
                interval = 60
                if 'interval' in options:
                    interval = options['interval']
                elif 'interval' in self.config['global']:
                    interval = self.config['global']['interval']

                jobs[name] = {
                    'method': job_obj.looped_method,
                    'interval': interval,
                }

            if hasattr(job_obj, 'build_items'):
                name = '-'.join([section, 'build_items'])
                interval = 60
                if 'interval' in options:
                    interval = options['interval']
                elif 'interval' in self.config['global']:
                    interval = self.config['global']['interval']

                jobs[name] = {
                    'method': job_obj.build_items,
                    'interval': interval,
                }

            if hasattr(job_obj, 'build_discovery_items'):
                name = '-'.join([section, 'build_discovery_items'])
                lld_interval = 600
                if 'lld_interval' in options:
                    lld_interval = options['lld_interval']
                elif 'lld_interval' in self.config['global']:
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
