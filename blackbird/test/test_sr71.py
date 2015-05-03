# -*- coding: utf-8 -*-

u"""
Tset sr71.py
"""

import glob
import os
import tempfile
import logging
from nose.tools import *

import blackbird.sr71
from blackbird.utils import configread


class TestJobCreater(object):

    def __init__(self):
        self.config = None
        self.jobs = None
        self.queue = None
        self.test_dir = 'test'

    def teardown(self):

        # remove dir for test.
        tmp_dirs = glob.glob('test/tmp*')

        for entry in tmp_dirs:
            os.removedirs(entry)

    def test_job_factory(self):
        # Start of creating mock objects
        module_path = tempfile.mkdtemp(dir=self.test_dir)
        module_path = os.path.abspath(module_path)
        job_str = (
            "class ConcreteJob(object):\n"
            "    def __init__(self, options=None, queue=None, logger=None):\n"
            "        pass\n"
            "    def build_items(self):\n"
            "        pass\n"
            "class Validator(object):\n"
            "    def __init__(self):\n"
            "        self.spec=(\n"
            "            '[hogehoge]',\n"
            "        )\n"
            "        self.module='hogehoge'\n"
            "\n"
        )

        job_mod = tempfile.NamedTemporaryFile(
            mode='w+',
            suffix='.py',
            dir=module_path
        )
        job_intermediate = os.path.basename(job_mod.name) + 'c'
        job_mod.write(job_str)
        job_mod.seek(0)

        cfg_str = (
            "[global]",
            "include = None",
            "module_dir = {module_path}".format(module_path=module_path),
            "max_queue_length = 1",
            "[hogehoge]",
            "module = {module_name}".format(
                module_name=os.path.basename(job_mod.name)[0:-3]
            ),
        )

        observer = configread.JobObserver()
        reader = configread.ConfigReader(cfg_str, observers=observer)
        creator = blackbird.sr71.JobCreator(
            reader.config,
            observer.jobs,
            logging
        )

        threads = creator.job_factory()

        # teardown remove tempfiles
        job_mod.close()
        os.remove(os.path.join(module_path, job_intermediate))

        value = 'hogehoge-build_items'
        ok_(value in threads.keys(),
            msg=('Failure to JobCreater.job_factory(), '
                 'Observer has {jobs}'
                 ''.format(jobs=threads)
                 )
            )
