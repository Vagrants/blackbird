# -*- coding: utf-8 -*-

"""
Zabbix sender plugin.
This plugin get the item from Queue and send the item to zabbix-server.
Beforehand, you need to map each key with Zabbix template.
"""

import json
import socket
import struct

from blackbird.plugins import base


class ConcreteJob(base.JobBase):
    def __init__(self, options, queue=None, stats_queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

        self.server_address = None
        self.set_server_address(options['server'])
        self.server_port = None
        self.set_server_port(options['port'])

        self.body = dict()
        self.body['request'] = 'sender data'
        self.body['data'] = list()
        self.result = None

        # Pool for when it fails to send.
        self.pool = list()

        # For blackbird's statistics
        self.stats_queue = stats_queue

    def build_items(self):
        """
        main loop
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
            self.logger.debug(self.body['data'])

            try:
                log_message = (
                    'Queue length is {0}'.format(len(self.body['data']))
                )
                self.logger.debug(log_message)
                if len(self.body['data']) != 0:
                    self.send(conn)
                    self.logger.debug(self.get_result())
            except:
                self._reverse_queue()
                log_message = (
                    'An error occurred.'
                    'Maybe socket error, or get invalid value.'
                )
                self.logger.debug(log_message)
            else:
                del self.body['data'][:]

        self.build_statistics_item()


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

    def build_statistics_item(self):
        """
        Statistics items are as following:
        * zabbix_sender result
            + processed, failed, total and more...
        """
        if self.result is not None:
            stats = dict()
            result = self.get_result()
            info = result['info']
            info = info.split(';')
            info = [entry.split(':') for entry in info]

            prefix = 'blackbird.zabbix_sender'

            for entry in info:
                key = entry[0].strip()
                value = None

                if key == 'processed':
                    value = int(entry[1])
                elif key == 'failed':
                    value = int(entry[1])
                elif key == 'total':
                    value = int(entry[1])
                elif key == 'seconds spent':
                    key = key.replace(' ', '_')
                    value = float(entry[1])
                    value *= 1000
                    value = str(round(value, 6))
                else:
                    log_message = (
                        'Blackbird has never seen {key}. {key} is new key??'
                        ''.format(key=key)
                    )
                    self.logger.info(log_message)

                if value is not None:
                    key = '.'.join([prefix, key])
                    stats[key] = value

            if 'response' in result:
                key = '.'.join([prefix, 'response'])
                stats[key] = result['response']

            for key, value in stats.iteritems():
                stats_key_list = [
                    'blackbird.zabbix_sender.processed',
                    'blackbird.zabbix_sender.failed',
                    'blackbird.zabbix_sender.total',
                ]
                item = BlackbirdStatisticsItem(
                    key=key,
                    value=value,
                    host=self.options['hostname']
                )
                if key in stats_key_list:
                    if self.enqueue(item=item, queue=self.stats_queue):
                        self.logger.debug(
                            'Inserted {0} to the statistics queue'
                            ''.format(item.data)
                        )
                else:
                    if self.enqueue(item=item, queue=self.queue):
                        self.logger.debug(
                            'Inserted {0} to the queue'.format(item.data)
                        )

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


class BlackbirdStatisticsItem(base.ItemBase):

    def __init__(self, key, value, host):
        super(BlackbirdStatisticsItem, self).__init__(key, value, host)

        self.__data = dict()
        self._generate()

    @property
    def data(self):

        return self.__data

    def _generate(self):
        self.__data['host'] = self.host
        self.__data['clock'] = self.clock
        self.__data['key'] = self.key
        self.__data['value'] = self.value


class Validator(base.ValidatorBase):
    u"""
    This class store information
    which is used by validation config file.
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "server = string()",
            "port = integer(0, 65535, default=10051)",
            "timeout = integer(default=4)",
            "hostname = string(default={0})".format(self.detect_hostname()),
        )
        return self.__spec


if __name__ == '__main__':
    ZABBIX_SENDER = ConcreteJob('127.0.0.1')
    ZABBIX_SENDER.send()
    print(ZABBIX_SENDER.get_result())
