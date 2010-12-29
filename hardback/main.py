#!/usr/bin/env python

import sys
import argparse
import hashlib
import cStringIO as StringIO

from . import *

WIDTH = 87

BUF_SIZE = 1000 # Must be divisible by 5


def enc_main(infile, outfile):
    h1 = hashlib.md5()
    h2 = hashlib.sha1()
    inp_len = 0
    inp = infile.read(BUF_SIZE)
    out = StringIO.StringIO()
    while inp:
        h1.update(inp)
        h2.update(inp)
        inp_len += len(inp)
        out.write(encode(inp))
        inp = infile.read(BUF_SIZE)
    out = out.getvalue()

    while out:
        outfile.write(out[:WIDTH] + '\n')
        out = out[WIDTH:]
    outfile.write('# length: %s, alphabet: %s\n# md5: %s, sha1: %s\n' % (inp_len, ALPHA, h1.hexdigest(), h2.hexdigest()))


def dec_main(infile, outfile, out_len):
    inp = []
    for line in infile:
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

    outfile.write(out)
    sys.stderr.write('# md5: %s, sha1: %s\n' % (h1.hexdigest(), h2.hexdigest()))


def main():
    parser = argparse.ArgumentParser(description='Hardcopy backup utility')
    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='input file')
    parser.add_argument('-o', '--output', dest='output', type=argparse.FileType('w'), default=sys.stdout, help='output file')
    parser.add_argument('-d', '--decode', dest='decode_len', type=int, help='decode with expected length DECODE_LEN')
    args = parser.parse_args()

    try:
        if args.decode_len is not None:
            dec_main(args.input, args.output, args.decode_len)
        else:
            enc_main(args.input, args.output)
    except Exception as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
