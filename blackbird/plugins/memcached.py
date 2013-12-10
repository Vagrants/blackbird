#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""\"memcached-tool 127.0.0.1:11211 stats\" to ZabbixServer."""

import telnetlib
from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    """
    This Class is called by "Executer"
    ConcreteJob is registerd as a job of Executer.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def looped_method(self):
        """
        Get stats data of memcached by using telnet.
        """

        conn = telnetlib.Telnet()
        conn.open(
            host=self.options['host'],
            port=self.options['port'],
            timeout=self.options['timeout']
        )

        conn.write('stats\n')
        result = conn.read_until('END').splitlines()
        conn.close()

        for line in result:
            if line.startswith('END'):
                break

            line = line.split()
            key = line[1]
            value = line[2]
            item = MemcachedItem(
                key=key,
                value=value,
                host=self.options['hostname']
            )

            self.queue.put(item, block=False)

            self.logger.debug(
                ('Inserted to queue memcached.{key}:{value}'
                 ''.format(key=key, value=value)
                 )
            )


class MemcachedItem(base.ItemBase):
    """
    Enqueued item.
    Take key(used by zabbix) and value as argument.
    """

    def __init__(self, key, value, host):
        super(MemcachedItem, self).__init__(key, value, host)

        self.__data = {}
        self._generate()

    @property
    def data(self):
        """Dequeued data."""

        return self.__data

    def _generate(self):
        """
        Convert to the following format:
        MemcachedItem(key='uptime', value='65535')
        {host:host, key:key1, value:value1, clock:clock}
        """

        self.__data['key'] = 'memcached.{0}'.format(self.key)
        self.__data['value'] = self.value
        self.__data['host'] = self.host
        self.__data['clock'] = self.clock


class Validator(base.ValidatorBase):
    """
    This class store information
    which is used by validation config file.
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "host = ipaddress(default='127.0.0.1')",
            "port = integer(0, 65535, default=11211)",
            "timeout = integer(default=10)",
            "hostname = string(default={0})".format(self.gethostname()),
        )
        return self.__spec
