# coding: utf-8

from __future__ import print_function
import time


def lazy_property(func):
    name = '_lazy_' + func.__name__

    @property
    def lazy(self, *args, **kwargs):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self, *args, **kwargs)
            setattr(self, name, value)
            return value
    return lazy


def log(*args, **kwargs):
    format_t = '%Y:%m:%d %H:%M:%S'
    local_t = time.localtime(time.time())
    dt = time.strftime(format_t, local_t)
    print(dt, *args, **kwargs)
