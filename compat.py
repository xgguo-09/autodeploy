# coding: utf-8
"""
python2 与 python3 兼容性代码
"""

import sys


__all__ = [
    'is_py3',
    'is_py2',
    'builtin_str',
    'bytes',
    'str',
    'basestring',
    'numeric_types',
    'integer_types',
    'input',
    'bytes2str',
    'next'
]


_ver = sys.version_info

# python2.x
is_py2 = (_ver[0] == 2)

# python3.x
is_py3 = (_ver[0] == 3)


if is_py2:
    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)
    integer_types = (int, long)

    input = raw_input

    def bytes2str(s):
        return s

    def next(iter_object):
        iter_object.next()
        return iter_object

elif is_py3:
    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)
    integer_types = (int,)

    input = input

    def bytes2str(s):
        return s.decode('utf-8') if isinstance(s, bytes) else s
    
    next = next
