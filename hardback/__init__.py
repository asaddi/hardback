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

import io
from zlib import crc32
import struct


__all__ = ['ALPHA', 'Error', 'encode', 'decode']


ALPHA = 'ybndrfg8ejkmcpqxot1uwisza345h769'
DE_ALPHA = {}
for i in range(len(ALPHA)):
    DE_ALPHA[ALPHA[i]] = i

# 20-bit CRC fits in 4 encoded characters
ENCODED_CRC_LEN = 4

# Smallest encode output (8 chars) + encoded CRC
MIN_LINE_LEN = 8+ENCODED_CRC_LEN

CRC_FORMAT = '<I'


class Error(Exception):
    pass


def raw_encode(s):
    out = io.StringIO()
    while s:
        ins = s[:5].ljust(5, b'\0')
        s = s[5:]
        ins = list(ins)
        ins.reverse()
        v = 0
        for x in ins:
            v <<= 8
            v |= x
        for i in range(8):
            out.write(ALPHA[v & 0x1f])
            v >>= 5
    return out.getvalue()


# CRC-20 with poly 0x1c4047
# Detects errors (up to and including Hamming distance 6)
# in 494 bits of data. Good enough for us (400 bits).
def crc_update(data, crc=0):
    for c in data:
        for i in (0x80, 0x40, 0x20, 0x10, 0x8, 0x4, 0x2, 0x1):
            bit = (crc & 0x80000) != 0
            if (c & i) != 0:
                bit = not bit
            crc <<= 1
            if bit:
                crc ^= 0xc4047
        crc &= 0xfffff
    return crc & 0xfffff


def encode(s, width=80):
    assert width % 8 == 0
    width = width * 5 // 8
    out = []
    crc = 0
    while s:
        ins = s[:width]
        s = s[width:]
        crc = crc_update(ins, crc)
        out.append(raw_encode(ins) + raw_encode(struct.pack(CRC_FORMAT, crc & 0xfffff))[:-4])
    return out


def raw_decode(s):
    out = io.BytesIO()
    while s:
        ins = s[:8].ljust(8, 'y')
        s = s[8:]
        ins = list(ins)
        ins.reverse()
        v = 0
        for c in ins:
            if c not in DE_ALPHA:
                raise Error("invalid character '%s'" % c)
            v <<= 5
            v |= DE_ALPHA[c]
        b = []
        for i in range(5):
            b.append(v & 0xff)
            v >>= 8
        out.write(bytes(b))
    return out.getvalue()


def decode(lines, length):
    out = io.BytesIO()
    lineNo = 0
    crc = 0
    for line in lines:
        lineNo += 1

        if len(line) < (8+ENCODED_CRC_LEN):
            raise Error('line too short at line %s' % lineNo)

        enc_crc = line[-ENCODED_CRC_LEN:]
        line = line[:-ENCODED_CRC_LEN]

        if len(line) % 8 != 0:
            raise Error('invalid line length (%s) at line %s' % (len(line)+ENCODED_CRC_LEN, lineNo))

        try:
            dec_line = raw_decode(line)[:length]
            dec_crc = raw_decode(enc_crc)
        except Error as e:
            raise Error('%s at line %s' % (str(e), lineNo))

        length -= len(dec_line)

        crc = crc_update(dec_line, crc)

        dec_crc = struct.unpack(CRC_FORMAT, dec_crc[:-1])[0]
        if crc != dec_crc:
            raise Error('CRC error at line %s' % lineNo)

        out.write(dec_line)
        if not length: break
    return out.getvalue()
