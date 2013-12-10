#!/usr/bin/env python
# -*- encodig: utf-8 -*-

u"""
Tset sr71.py
"""

import glob
import os
import tempfile
from nose.tools import *

import sr71
from utils import configread


class TestJobCreater(object):

    def __init__(self):
        self.config = None
        self.jobs = None
        self.queue = None
        self.test_dir= 'tests'

    def teardown(self):
      
        # remove dir for test.
        tmp_dirs = glob.glob('tests/tmp*')

        for dir in tmp_dirs:
            os.removedirs(dir)

    def test_job_factory(self):
        #Start of creating mock objects
        module_path = tempfile.mkdtemp(dir=self.test_dir)
        cfg_str = (
            "[global]",
            "include = None",
            "module_path = {module_path}".format(module_path=module_path),
            "[hogehoge]",
            "module = hogehoge",
        )

        job_str = (
            "class ConcreteJob(object):\n"
            "    def __init__(self, options, queue):\n"
            "        pass\n"
            "class Validator(object):\n"
            "    def __init__(self):\n"
            "        self.spec=(\n"
            "            '[hogehoge]',\n"
            "        )\n"
            "        self.module='hogehoge'\n"
            "\n"
        )

        job_mod = tempfile.NamedTemporaryFile(mode='r+',
                                              suffix='.py',
                                              dir=module_path
                                              )
        job_intermediate = os.path.basename(job_mod.name) + 'c'

        job_mod.write(job_str)
        job_mod.seek(0)
        #End of creating mock objects

        observer = configread.JobObserver() 
        reader = configread.ConfigReader(cfg_str, observers=observer)
        creater = sr71.JobCreater(reader.config,
                                  observer.jobs,
                                  'Queue')

        threads = creater.job_factory()

        #teardown remove tempfiles
        job_mod.close()
        os.remove(os.path.join(module_path, job_intermediate))

        checked_name = 'ConcreteJob'
        eq_(threads[0].job.__class__.__name__,
            checked_name,
            msg=('Failure to JobCreater.job_factory(), '
                 'Observer has {jobs}'
                 ''.format(jobs=threads)
                 )
            )
