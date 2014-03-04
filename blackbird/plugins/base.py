# -*- coding: utf-8 -*-

"""Various Base objects"""

import abc
import datetime
import json
import math
import socket
import time

from Queue import Full


class JobBase(object):
    u"""Based ConcreteJob"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, options, queue, logger):
        self.options = options
        self.queue = queue
        self.logger = logger
        self.invalid_key_list = None

    # TODO: looped_method to build_items
    #@abc.abstractmethod
    #def looped_method(self):
        #raise NotImplementedError

    def enqueue(self, item, queue=None):
        """
        Enqueue items.
        If you define "self.filter" (sequence),
        this method put the item to queue after filtering.
        "self.filter" operates as blacklist.

        This method expects that
        "item" argument has dict type "data" attribute.
        """
        if queue is None:
            queue = self.queue
        is_enqueue_item = True

        if self.invalid_key_list is not None:
            for entry in self.invalid_key_list:
                if entry in item.data['key']:
                    is_enqueue_item = False
                    log_message = (
                        '{key} is filtered by "invalid_key_list".'
                        ''.format(key=item.data['key'],
                                  plugin=__name__)
                    )
                    self.logger.debug(log_message)
                    break

        if is_enqueue_item:
            try:
                queue.put(item, block=False)
                return True
            except Full:
                self.logger.error('Blackbird item Queue is Full!!!')
                return False

        else:
            return False


class ItemBase(object):
    """
    Base class of the item to be enqueued.
    This class has row value(key, value...and more).
    When it is dequeue, it assemble appropriate format.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, key=None, value=None, host=None, clock=None):
        self.key = key
        self.value = value
        self.host = host
        self.clock = self.__set_timestamp(clock)

    @abc.abstractproperty
    def data(self):
        u"""Dequeued data."""
        raise NotImplementedError

    def _generate(self):
        u"""overrided in each modules."""

        self._data['key'] = self.key
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock

    def __set_timestamp(self, clock):
        """
        If "clock" is None, set the time now.
        This function is called self.__init__()
        """
        if clock == None:
            unix_timestamp = time.mktime(datetime.datetime.now().utctimetuple())
            timestamp = int(unix_timestamp)

            return timestamp

        else:
            return clock


class DiscoveryItem(ItemBase):
    """
    Low Level Discovery item.
    LLD item has following json format:
        {
            'host': 'exmaple.com',
            'value': {
                'data': [{'{#MACRO_NAME}': 'hogehoge001'}, {'{#MACRO_NAME}': 'hogehoge002'}],
            'key': 'YOUR_LLD_KEYNAME',
            'clock': 946652400
        }

    "value" argument must be list or tuple type object which has dictionaries.
    e.x:
        item = DiscoveryItem(
            key='sample.LLD',
            value=[
                {'{#HOSTNAME}': 'hogehoge.com'},
                {'{#HOSTNAME}': 'hogehoge.org'}
            ],
            host='YOUR_ZABBIX_HOSTNAME'
        )
    """

    def __init__(self, key, value, host, clock=None):
        super(DiscoveryItem, self).__init__(key, value, host)

        self.__data = dict()
        self._generate()

    @property
    def data(self):
        return self.__data

    def _generate(self):
        self.__data['host'] = self.host
        self.__data['clock'] = self.clock
        self.__data['key'] = self.key

        value = {
            'data': self.value
        }
        self.__data['value'] = json.dumps(value)


class BlackbirdPluginError(Exception):
    """
    blackbird error object.
    When an error occurs in plugin module,
    you should not raise built-in errors but this error.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ValidatorBase(object):
    """
    e.g: check the validity of the values as follows:
    host -> '127.0.0.1'(IPAddress),
    port -> '11211'(number of 0 - 65535)
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def spec(self):
        """
        "spec" property is used When "ConfigReader" validates config file.
        "spec" property must be listed configobj's specfiles rules.
        e.g:
        [redis]
        host = ipaddress(default='127.0.0.1')
        port = port(0, 65535, default=6379)

        "configspec" as ConfigObj's argument must be
        file-like object(like StringIO or TemporaryFile)
        or a list of lines.

        Notes: 1. List of lines as COnfigObj's argument
        Both following format works fine.

        spec = (
            "[redis]",
            "host = string(default='127.0.0.1')",
            "port = integer(0, 6535, default=6379)"
        )

        spec = (
            "[redis]\n",
            "host = string(default='127.0.0.1')\n",
            "port = integer(0, 6535, default=6379)\n"
        )

        Notes: 2. file-like object
        You can also use file-like object.
        Both following format works fine.

        spec = (
            "[redis]\n"
            "host = string(default='127.0.0.1')\n"
            "port = integer(0, 65535, default=6379)\n"
        )
        io = StringIO.StringIO()
        io.write(spec)
        io.flush()
        io.seek(0)

        spec = (
            "[redis]\n",
            "host = string(default='127.0.0.1')\n",
            "port = integer(0, 65535, default=6379)\n"
        )
        io = StringIO.StringIO()
        io.write(spec)
        io.flush()
        io.seek(0)
        """

        raise NotImplementedError('spec')

    def detect_hostname(self):
        return socket.getfqdn() or socket.gethostname() or 'localhost'

class Timer(object):
    """
    TImer Context mansger class.
    Usage:
        with Timer() as timer:
            YOUR_EXECUTE

        print timer.sec
        print timer.msec
    """

    def __init__(self):
        pass

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        diff = self.end - self.start
        if diff < 0:
            diff = 0

        self.sec = str(round(diff, 6))
        self.msec = str(round(diff * 1000, 6))
