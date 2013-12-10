#!/usr/bin/env python
# -*- encodig: utf-8 -*-

import socket

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

        self.host = socket.gethostbyname(options['host'])
        self.port = options['port']
        self.addr = (self.host, self.port)
        self.timeout = options['interval'] / 2
        self.sock = None

        self.hostname = options['hostname']

    def looped_method(self):
        u"""
        Main method.

        This method execute the process as following:
            1. get munin-node's all plugins
            2. get executing result of all plugins
            3. convert result of "2"
               "fetch plugin" cmmand of munin-node return key:value.
               key:value -> {timestamp, zabbix-host, zabbix-key, value}
            4. push the converted result to queue
        """

        self.connect()

        for method in self.get_plugins():
            writer = self.sock.makefile('wb')
            writer.write('fetch {0}\r\n'.format(method))
            writer.close()

            reader = self.sock.makefile('rb')

            while True:
                line = reader.readline().strip()

                if not line:
                    break
                elif line.startswith('#'):
                    continue
                elif line == '.':
                    break
                else:
                    line = line.split()
                    item = MuninNodeItem(key=line[0],
                                         value=line[1],
                                         host=self.hostname)

                    if self.queue:
                        self.queue.put(item, block=False)
                        self.logger.debug(
                            ('Inserted to queue munin_node.{key}:{value}'
                             ''.format(key=key, value=value)
                             )
                        )
                    self.logger.info('Enqueued MuninNodeItem')

            reader.close()

        self.close()

    def connect(self):
        u"""
        Create connection with "munin-node"
        munin-node returns "munin node at HOSTNAME" and usage as hello-message.

        So, "reader.readline()" consume munin-node's hello-message.
        """

        self.sock = socket.create_connection(self.addr, timeout=self.timeout)

        reader = self.sock.makefile('rb')
        reader.readline()
        reader.close()

    def get_plugins(self):
        u"""
        Get munin-node's enabled plugins.
        """

        writer = self.sock.makefile('wb')
        writer.write('list\r\n')
        writer.close()

        reader = self.sock.makefile('rb')

        plugins = reader.readline().strip()
        plugins = plugins.split()

        reader.close()
        return plugins

    def close(self):
        self.sock.close()


class MuninNodeItem(base.ItemBase):

    def __init__(self, key, value, host):
        super(MuninNodeItem, self).__init__(key, value, host)

        self.__data = {}
        self._generate()

    @property
    def data(self):

        return self.__data

    def _generate(self):

        self.__data['key'] = 'munin.{0}'.format(self.key)
        self.__data['value'] = self.value
        self.__data['host'] = self.host
        self.__data['clock'] = self.clock


class Validator(base.ValidatorBase):
    u"""
    This class store information
    which is used by validation config file.
    """

    def __init__(self):
        self.__spec = None
        self.__module = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "host = ipaddress(default='127.0.0.1')",
            "port = integer(0, 65535, default=4949)",
            "interval = integer(30, 86400, default=30)",
            "hostname = string(default={0})".format(self.gethostname()),
        )

        return self.__spec


if __name__ == '__main__':
    OPTIONS = {
        'host': '127.0.0.1',
        'port': 4949,
        'interval': 10,
        'hostname': '127.0.0.1'
    }
    JOB = ConcreteJob(OPTIONS)
    JOB.looped_method()
