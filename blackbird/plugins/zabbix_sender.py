#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""zabbix_sender utility.

This module implements zabbix_sender command line utility in pure python.

Example:

>>> import utils.ZabbixSender
>>> zabbix_sender = utils.ZabbixSender.ZabbixSender('127.0.0.1')
>>> zabbix_sender.set_hostname('test_host')
>>> zabbix_sender.add('test_key1', 'test_value1')
>>> zabbix_sender.add('test_key2', 'test_value2')
>>> zabbix_sender.send()
    >>> print(zabbix_sender.get_result())
{u'info': u'Processed 2 Failed 0 Total 2 Seconds spent 0.000111', u'response': u'success'}
"""

import json
import socket
import struct

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

        self.server_address = None
        self.set_server_address(options['Server'])
        self.server_port = None
        self.set_server_port(options['port'])

        self.body = dict()
        self.body['request'] = 'sender data'
        self.body['data'] = list()

        # Pool for when it fails to send.
        self.pool = list()

        self.result = None

    def looped_method(self):
        u"""
        The method is called from "Executer" as following:
        while True:
            self.job.looped_method()

        self.pool is place where save temporary items in the queue
        when some error occur.
        """

        conn = self.connect(address=self.server_address, port=self.server_port)

        if conn:

            while not self.queue.empty():
                item = self.queue.get()
                self.pool.append(item)
                if type(item.data) is (tuple or list):
                    self.body['data'].extend(item.data)
                else:
                    self.body['data'].append(item.data)
            # debug
            self.logger.debug(self.body['data'])

            try: 
                print len(self.body['data'])
                if len(self.body['data']) != 0:
                    self.send(conn)
                    self.logger.debug(self.get_result())
            except:
                self._reverse_queue()
                self.logger.debug(
                    ('An error occured. Maybe socket error, or get invalid value.')
                )
            else:
                del self.body['data'][:]


    def connect(self, address, port):
        try:
            conn = socket.create_connection(
                (self.server_address, self.server_port),
                timeout=self.options['timeout']
            )
            return conn
        except socket.error:
            return False

    def send(self, sock):
        request = json.dumps(self.body, ensure_ascii=False).encode('utf-8')
        fmt = '<4sBQ' + str(len(request)) + 's'
        data = struct.pack(fmt, 'ZBXD', 1, len(request), request)
 
        writer = sock.makefile('wb')
        writer.write(data)
        writer.close()
 
        reader = sock.makefile('rb')
        response = reader.read()
        reader.close()
 
        sock.close()
 
        fmt = '<4sBQ' + str(len(response) - struct.calcsize('<4sBQ')) + 's'
        self.result = struct.unpack(fmt, response)

        del self.pool[:]

    def get_result(self):
        return json.loads(self.result[3])

    def _reverse_queue(self):
        u"""When socket.timeout has occurred for Zabbix server,
        this method is called.
        Enqueue items in self.pool[].
        """

        while self.pool:
            item = self.pool.pop()
            self.queue.put(item, block=False)

    def set_server_port(self, port):
        """
        Set self.server_port.
        """

        self.server_port = port

    def set_server_address(self, address):
        """
        Set self.server_address.
        """

        self.server_address = socket.gethostbyname(address)

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
            "Server = string()",
            "port = integer(0, 65535, default=10051)",
            "timeout = integer(default=4)",
            "hostname = string(default={0})".format(self.gethostname()),
        )
        return self.__spec


if __name__ == '__main__':
    ZABBIX_SENDER = ConcreteJob('127.0.0.1')
    ZABBIX_SENDER.send()
    print(ZABBIX_SENDER.get_result())
