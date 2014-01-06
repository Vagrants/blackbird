#!/usr/bin/env python
# -*- encodig: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils import setup

setup(
    name='blackbird',
    version='0.3.1',
    description='Daemon monitoring each middleware by using ZABBIX-SENDER',
    author='ARASHI, Jumpei',
    author_email='jumpei.arashi@arashike.com',
    url='https://github.com/Vagrants/blackbird',
    packages=[
        'blackbird',
        'blackbird.plugins',
        'blackbird.utils',
    ],
    entry_points={
        'console_scripts': ['blackbird = blackbird.sr71:main']
    }
)
