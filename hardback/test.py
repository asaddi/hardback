#!/usr/bin/env python
# Copyright 2010 Allan Saddi <allan@saddi.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os

from hardback import *


def test():
    for i in range(1, 4000):
        test_str = os.urandom(i)
        enc = encode(test_str)
        dec = decode(enc, i)
        if test_str == dec:
            sys.stdout.write('.')
        else:
            sys.stdout.write('X')
        sys.stdout.flush()
    sys.stdout.write('\n')


if __name__ == '__main__':
    test()
