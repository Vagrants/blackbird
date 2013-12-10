#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""Put "redis-cli info" to Queue"""

from blackbird.plugins import base
from blackbird.utils.helpers import global_import

class ConcreteJob(base.JobBase):
    u"""This Class is called by "Executer".
    The thread to be called,
    it is necessary to implement "ConcreteJob" and "looped_method".
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

        self.connection = self.create_connection(options)
        self.hostname = options['hostname']

    def looped_method(self):
        for key, value in self.connection.info().items():
            item = RedisItem(key=key,
                             value=value,
                             host=self.hostname)

            self.queue.put(item, block=False)

            self.logger.debug(
                ('Inserted to queue redis.{key}:{value}'
                 ''.format(key=key, value=value)
                 )
            )
        self.logger.info('Enqueued RedisItem.')

    @staticmethod
    def create_connection(options):
        u"""
        Create a connection for redis.
        Validation of the values is done in ConfigReader._validate().
        """
        redis = global_import('redis')

        connection = redis.Redis(host=options['host'],
                                 port=options['port'],
                                 db=options['db'],
                                 password=options['password'],
                                 charset=options['charset']
                                 )
        connection.ping()
    
        return connection

class RedisItem(base.ItemBase):
    u"""Enqueued item. Take arguments as 
    key, value pair of redis.info().items.
    """

    def __init__(self, key, value, host):
        super(RedisItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        u"""Dequeued data. DictType object.
        {key1:value1, key2:value2, host=host, clock=clock}
        """

        return self._data

    def _generate(self):
        u"""redis.info() return [{key1:value1}, {key2:value2}...]
        Convert to the following format:
        redis.info() -> {host:host, key:key, value:value, clock:clock}
        """

        self._data['key'] = 'redis.{0}'.format(self.key)
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock

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
            "port = integer(0, 65535, default=6379)",
            "db = integer(default=0)",
            "password = string(default=None)",
            "charset = string(default='utf-8')",
            "hostname = string(default={0})".format(self.gethostname()),
        )
        return self.__spec
