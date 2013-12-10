#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""main process."""

import Queue
import threading
import time
from daemon import DaemonContext

from blackbird.utils import argumentparse
from blackbird.utils import configread
from blackbird.utils import logger

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
    utils/configread parse and read config file,
    collect job(thread) that is written in config file.
    This process make the start of each jobs(threads).
    """

    def __init__(self):
        self.config = CONFIG
        self.logger = self._set_logger()
        self.queue = Queue.Queue()
        self.threads = []

        self._create_threads()

    def _set_logger(self):
        logger_obj = logger.logger_factory(self.config['global']['log_file'],
                                           self.config['global']['log_level']
                                           )
        return logger_obj

    def _create_threads(self):
        u"""
        This method create threads from self.jobs.
        """

        creater = JobCreater(self.config, JOBS.jobs, self.queue, self.logger)

        self.threads.extend(creater.job_factory())

    def start(self):

        log_file = open(self.config['global']['log_file'], 'a+', 0)
        self.logger.info('stated  process main')
        pid_file = pidlockfile.PIDLockFile(self.config['global']['pid_file'])

        if not ARGS.debug_mode:
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
                for thread in self.threads:
                    thread.start()

                while True:
                    for thread in self.threads:
                        thread.join(1)

        else:
            for thread in self.threads:
                thread.start()

            while True:
                for thread in self.threads:
                    thread.join(1)


class JobCreater(object):
    u"""
    JobFactory class.
    job class(ConcreteJob) -> job instance(threads that BlackBird starts).
    """

    def __init__(self, config, jobs, queue, logger):
        self.config = config
        self.jobs = jobs
        self.queue = queue
        self.logger = logger

    def job_factory(self):
        u"""
        This method is Factory method.
        Take list of jobs and queue as arguments.
        list of jobs is list of "ConcreteJob" classes.
        Return list of threads.
        """

        threads = []

        for section, options in self.config.items():

            if section == 'global':
                continue

            #Since validate in utils/configread, does not occur here Error
            #In the other sections are global,
            #that there is a "module" option is collateral.
            name = options['module']

            job_kls = self.jobs[name]
            job_obj = job_kls(options, self.queue, self.logger)

            if 'interval' in options:
                threads.append(Executer(job_obj,
                                        name=section,
                                        interval=options['interval']
                                        )
                               )

            else:
                threads.append(Executer(job_obj, name=section))
        return threads


class Executer(threading.Thread):
    u"""
    job executer class.
    "interval" argument is interval of getting data.

    If you write "interval" option as following at each section in config file:
        interval = 30

    Executer get the data every 30 seconds.
    """
    def __init__(self,
                 job,
                 name=None,
                 interval=10
                 ):
        threading.Thread.__init__(self, name=name)
        self.setDaemon(True)

        self.job = job
        self.interval = interval

    def run(self):
        while True:
            self.job.looped_method()

            time.sleep(self.interval)


def main():
    sr71 = BlackBird()
    sr71.start()


if __name__ == '__main__':
    main()
