#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import blackbird

setup(
    name='blackbird',
    version=blackbird.__version__,
    description='Daemon that monitor each middleware by using ZABBIX-SENDER',
    author='ARASHI, Jumpei',
    author_email='jumpei.arashi@arashike.com',
    url='https://github.com/Vagrants/blackbird',
    license='WTFPL',
    packages=[
        'blackbird',
        'blackbird.plugins',
        'blackbird.utils',
    ],
    entry_points={
        'console_scripts': ['blackbird = blackbird.sr71:main']
    },
    install_requires=[
        "argparse",
        "configobj",
        "ipaddr",
        "lockfile",
        "logilab-astng",
        "logilab-common",
        "python-daemon",
    ],
    tests_require=[
        'nose',
        "unittest2",
    ],
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
