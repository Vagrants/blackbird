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

    parser.add_argument('--debug_mode', '-d',
                        action='store_true',
                        help='Turn on debug mode'
                        )

    parser.add_argument('--pid_file', '-p',
                        default='/var/run/blackbird/blackbird.pid',
                        help='pid file location'
                        )

    return parser.parse_args()
