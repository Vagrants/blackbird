#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse


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
                        default='/var/run/blackbird/blackbird.pid',
                        help='pid file location',
                        dest='pid_file'
                        )

    parser.add_argument('--ignore-plugindir', '-P',
                        action='store_true',
                        dest='ignore_plugindir',
                        help='Don\'t check to exists plugin dir.'
                        )

    return parser.parse_args()
