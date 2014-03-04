# -*- coding: utf-8 -*-

"""
Blackbird statistics plugins.
This plugin get the items queue for "stats" and
put the items queue for "item".
"""

import blackbird
from blackbird.plugins import base

class ConcreteJob(base.JobBase):
    def __init__(self, options, queue=None, stats_queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

        self.stats = {
            'blackbird.ping': 1,
            'blackbird.version': blackbird.__version__,
            'blackbird.queue.length': None,
            'blackbird.zabbix_sender.processed': 0,
            'blackbird.zabbix_sender.failed': 0,
            'blackbird.zabbix_sender.total': 0,
        }
        self.stats_queue = stats_queue

    def build_items(self):
        """
        get the items from STATS QUEUE
        calculate self.stats
        make new items from self.stats
        put the new items for ITEM QUEUE
        """
        while not self.stats_queue.empty():
            item = self.stats_queue.get()
            self.calculate(item)

        for key, value in self.stats.iteritems():
            if 'blackbird.queue.length' == key:
                value = self.queue.qsize()
            item = BlackbirdStatisticsItem(
                key=key,
                value=value,
                host=self.options['hostname']
            )
            if self.enqueue(item=item, queue=self.queue):
                self.logger.debug(
                    'Inserted {0} to the queue.'.format(item.data)
                )

    def calculate(self, item):
        if 'key' in item.data:
            if item.data['key'] in self.stats.keys():
                key = item.data['key']
                self.stats[key] += item.data['value']


class BlackbirdStatisticsItem(base.ItemBase):

    def __init__(self, key, value, host):
        super(BlackbirdStatisticsItem, self).__init__(key, value, host)
        self._data = dict()
        super(BlackbirdStatisticsItem, self)._generate()

    @property
    def data(self):
        return self._data


class Validator(base.ValidatorBase):

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "hostname = string(default={0})".format(self.detect_hostname())
        )
        return self.__spec
