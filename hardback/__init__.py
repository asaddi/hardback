import cStringIO as StringIO
from zlib import crc32
import struct


__all__ = ['ALPHA', 'Error', 'encode', 'decode']


ALPHA = '0123456789ACDEFGHJKLMNPRSTUVWXYZ'
DE_ALPHA = {}
for i in range(len(ALPHA)):
    DE_ALPHA[ALPHA[i]] = i

# 32-bit CRC fits in 7 encoded characters (35-bits)
ENCODED_CRC_LEN = 7

# Smallest encode output (8 chars) + encoded CRC
MIN_LINE_LEN = 8+ENCODED_CRC_LEN

CRC_FORMAT = '<i'


class Error(Exception):
    pass


def raw_encode(s):
    out = StringIO.StringIO()
    while s:
        ins = (s[:5] + '\x00' * 4)[:5]
        s = s[5:]
        ins = [ord(x) for x in ins]
        ins.reverse()
        v = 0L
        for x in ins:
            v <<= 8
            v |= x
        for i in range(8):
            out.write(ALPHA[v & 0x1F])
            v >>= 5
    return out.getvalue()


def encode(s, width=80):
    assert width % 8 == 0
    width = width * 5 / 8
    out = []
    crc = 0
    while s:
        ins = s[:width]
        s = s[width:]
        crc = crc32(ins, crc)
        out.append(raw_encode(ins) + raw_encode(struct.pack(CRC_FORMAT, crc))[:-1])
    return out


def raw_decode(s):
    out = StringIO.StringIO()
    while s:
        ins = (s[:8] + '0' * 7)[:8]
        s = s[8:]
        ins = [x for x in ins]
        ins.reverse()
        v = 0L
        for c in ins:
            if c not in DE_ALPHA:
                raise Error, "invalid character '%s'" % c
            v <<= 5
            v |= DE_ALPHA[c]
        for i in range(5):
            out.write(chr(v & 0xFF))
            v >>= 8
    return out.getvalue()


def decode(lines, length):
    out = StringIO.StringIO()
    lineNo = 0
    crc = 0
    for line in lines:
        lineNo += 1

        if len(line) < (8+ENCODED_CRC_LEN):
            raise Error, 'line too short at line %s' % lineNo

        enc_crc = line[-ENCODED_CRC_LEN:]
        line = line[:-ENCODED_CRC_LEN]

        if len(line) % 8 != 0:
            raise Error, 'invalid line length (%s) at line %s' % (len(line)+ENCODED_CRC_LEN, lineNo)

        try:
            dec_line = raw_decode(line)[:length]
            dec_crc = raw_decode(enc_crc)
        except Error as e:
            raise Error, '%s at line %s' % (str(e), lineNo)

        length -= len(dec_line)

        crc = crc32(dec_line, crc)

        dec_crc = struct.unpack(CRC_FORMAT, dec_crc[:-1])[0]
        if crc != dec_crc:
            raise Error, 'CRC error at line %s' % lineNo

        out.write(dec_line)
        if not length: break
    return out.getvalue()
