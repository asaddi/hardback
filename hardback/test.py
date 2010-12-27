#!/usr/bin/env python

import sys
import os

from hardback import *


def test():
    for i in range(1, 4000):
        test_str = os.urandom(i)
        enc = encode(test_str)
        dec = decode(enc)[:i]
        if test_str == dec:
            sys.stdout.write('.')
        else:
            sys.stdout.write('X')
        sys.stdout.flush()
    sys.stdout.write('\n')


if __name__ == '__main__':
    test()
