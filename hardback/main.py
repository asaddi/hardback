#!/usr/bin/env python

import sys
import getopt
import hashlib
import cStringIO as StringIO

from . import *

WIDTH = 87

BUF_SIZE = 1000 # Must be divisible by 5


def enc_main():
    h1 = hashlib.md5()
    h2 = hashlib.sha1()
    inp_len = 0
    inp = sys.stdin.read(BUF_SIZE)
    out = StringIO.StringIO()
    while inp:
        h1.update(inp)
        h2.update(inp)
        inp_len += len(inp)
        out.write(encode(inp))
        inp = sys.stdin.read(BUF_SIZE)
    out = out.getvalue()

    while out:
        sys.stdout.write(out[:WIDTH] + '\n')
        out = out[WIDTH:]
    sys.stdout.write('# length: %s, alphabet: %s\n# md5: %s, sha1: %s\n' % (inp_len, ALPHA, h1.hexdigest(), h2.hexdigest()))


def dec_main(out_len):
    inp = []
    for line in sys.stdin:
        line = line.strip()
        if line.startswith('#'): continue
        inp.append(line)
    inp = ''.join(inp)

    out = decode(inp)

    if len(out) < out_len:
        raise RuntimeError, 'input not long enough'

    out = out[:out_len]

    h1 = hashlib.md5()
    h2 = hashlib.sha1()
    h1.update(out)
    h2.update(out)

    sys.stdout.write(out)
    sys.stderr.write('# md5: %s, sha1: %s\n' % (h1.hexdigest(), h2.hexdigest()))


def main():
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'd:')

        do_decode = False
        decode_len = 0
        for opt, arg in optlist:
            if opt == '-d':
                do_decode = True
                decode_len = int(arg)

        if do_decode:
            dec_main(decode_len)
        else:
            enc_main()
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
