#!/bin/env python
from __future__ import print_function
class Timer(object):
    def __init__(self, print_func=print, start_msg=None):
        """
        example:
        with Timer(start_msg='start') as t:
            t.elapsed_str

        :param print_func: how to print the msg
        :param start_msg: start msg
        """
        self.start_msg = start_msg
        self.print_func = print_func
        self.start = 0

    def __enter__(self):
        if self.start_msg:
            self.print_func(self.start_msg)
        self.start = default_timer()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is not None:
            self.print_func(exc_value)

    def reset(self):
        self.start = default_timer()

    @property
    def elapsed(self):
        return default_timer() - self.start

    @property
    def elapsed_str(self):
        return 'elapsed {:.4f}s'.format(self.elapsed)
