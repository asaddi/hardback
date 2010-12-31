#!/usr/bin/env python

import sys
import argparse
import hashlib
import cStringIO as StringIO

from . import *


WIDTH = 80


def enc_main(infile, outfile):
    inp = infile.read()
    h1 = hashlib.md5(inp)
    h2 = hashlib.sha1(inp)
    out = encode(inp, width=WIDTH)

    for line in out:
        outfile.write(line + '\n')
    outfile.write('# length: %s, alphabet: %s, CRC-32 poly: 0x4C11DB7\n# md5: %s, sha1: %s\n' % (len(inp), ALPHA, h1.hexdigest(), h2.hexdigest()))


def dec_main(infile, outfile, out_len):
    lines = []
    for line in infile:
        line = line.strip()
        if line.startswith('#'): continue
        lines.append(line)

    out = decode(lines, out_len)

    if len(out) < out_len:
        raise Error, 'input not long enough'

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
    except Error as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
