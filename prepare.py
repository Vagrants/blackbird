#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import subprocess
import sys

try:
    import pydoc
except ImportError:
    print('Sorry. Please install "pydoc".')
    sys.exit()

from string import find


PRE_COMMIT = """#!/usr/bin/python

import sys
import re
import subprocess

modified = re.compile('^(?:M|A)..(?P<name>.*\.py)')


def main():
    p = subprocess.Popen(['git', 'status', '--porcelain'],
                         stdout=subprocess.PIPE)
    out, err = p.communicate()
    modifieds = []
    for line in out.splitlines():
        match = modified.match(line)
        if (match):
            modifieds.append(match.group('name'))

    rrcode = 0
    for file in modifieds:
        p = subprocess.Popen(['pep8', file],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out or err:
            sys.stdout.write(" * pep8:\\n%s\\n%s" % (out, err))
            rrcode = rrcode | 1
        retcode = subprocess.call(['pyflakes', file])
        rrcode = retcode | rrcode

    sys.exit(rrcode)

if __name__ == '__main__':
    main()
"""


def get_modules():
    """
    Get the all available python-modules.
    """

    modules = list()

    def callback(path, modname, desc, modules=modules):
        if modname and modname[-9:] == '.__init__':
            modname = modname[:-9]
        if find(modname, '.') < 0 and modname not in modules:
            modules.append(modname)

    def onerror(modname):
        callback(None, modname, None)

    pydoc.ModuleScanner().run(callback, onerror=onerror)
    return modules


def pip_install(packages):
    if type(packages) == str:
        subprocess.check_call(
            ['pip', 'install', '-U', packages]
        )
    elif (type(packages) == list) or (type(packages) == tuple):
        for package in packages:
            subprocess.check_call(
                ['pip', 'install', '-U', packages]
            )


if __name__ == '__main__':
    if not '.git' in os.listdir(os.path.curdir):
        raise OSError(errno.ENOENT, '.git:No such or directory.')

    MODULES = get_modules()
    REQUIRES = ['pep8', 'pyflakes']

    if not 'pip' in MODULES:
        print('Please install "pip". e.x:yum install python-pip')
        sys.exit()
    for require_pkg in REQUIRES:
        if not require_pkg in MODULES:
            pip_install(require_pkg)
    pre_commit_file = open('.git/hooks/pre-commit', 'w')
    pre_commit_file.writelines(PRE_COMMIT)
    pre_commit_file.close()
