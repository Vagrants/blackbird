# -*- coding: utf-8 -*-
u"""Parse /proc/net/"protocol" and put Queue"""

import os

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    u"""This Class is called by "Executer".
    ConcreteJob is registerd as a job of Executer.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options,
                                          queue,
                                          logger
                                          )

        self.hostname = options['hostname']

    def build_items(self):
        u"""This method called by Executer.
        /proc/net/tcp -> {host:host, key:key, value:value, clock:clock}
        """
        protocols = ['tcp', 'tcp6']
        for protocol in protocols:
            procfile = open('/proc/net/{0}'.format(protocol), 'r')
            stats = self.count(procfile)

            for key, value in stats.items():
                item = NetstatItem(key=key,
                                   value=value,
                                   host=self.hostname
                                   )

                self.queue.put(item, block=False)

    @staticmethod
    def count(procfile):
        u"""Take arguments as intermediate data.
        {protocol:[...]} -> {key1:value1, key2:value2}
        e.g: {linux.net.tcp.LISTEN: 20}
        """

        state_tcp = {
            '01': 'ESTABLISHED',
            '02': 'SYN_SENT',
            '03': 'SYN_RECV',
            '04': 'FIN_WAIT1',
            '05': 'FIN_WAIT2',
            '06': 'TIME_WAIT',
            '07': 'CLOSE',
            '08': 'CLOSE_WAIT',
            '09': 'LAST_ACK',
            '0A': 'LISTEN',
            '0B': 'CLOSING',
        }

        protocol = os.path.basename(procfile.name)

        state = []
        stats = {}

        # read procfile. e.g: /proc/net/tcp -> ['0A', '0A', '06', '01', '0A']
        for line in procfile.readlines():
            state.append(line.split()[3])

        for state_type, state_name in state_tcp.items():
            key = 'linux.net.{proto}[{state}]'.format(proto=protocol,
                                                      state=state_name
                                                      )
            value = state.count(state_type)
            stats[key] = value

        procfile.close()
        return stats


class NetstatItem(base.ItemBase):
    u"""Enqueued item. Take an argument as redis.info()."""

    def __init__(self, key, value, host):
        super(NetstatItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        u"""Dequeued data. ListType object.
        [{key1:value1}, {key2:value2}...]
        """

        return self._data


class Validator(base.ValidatorBase):
    def __init__(self):
        self.__spec = None
        self.__module = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "hostname = string(default={0})".format(self.detect_hostname()),
        )
        return self.__spec
