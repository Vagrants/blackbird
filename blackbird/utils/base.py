# -*- coding: utf-8 -*-
u"""Base class used under the utils directory."""

import abc

class Observer(object):
    u"""Base class called Observer in Gof"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self):
        u"""
        This method is called by Subject.notify().
        Update the state of Subject.
        """

        raise NotImplementedError

class Subject(object):
    u"""Base class called Subject in Gof"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def register(self, observer):
        u"""
        This method register Observer to Subject.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def unregister(self, observer):
        u"""
        This method unregister Observer to Subject.c
        """

        raise NotImplementedError

    @abc.abstractmethod
    def notify(self):
        u"""
        This method call Observer.update().
        Notify the own status.
        """

        raise NotImplementedError
