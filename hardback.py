#!/usr/bin/env python

import cStringIO as StringIO


alpha = '0123456789ACDEFGHJKLMNPRSTUVWXYZ'
de_alpha = {}
for i in range(len(alpha)):
    de_alpha[alpha[i]] = i


def encode(s):
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
            out.write(alpha[v & 0x1F])
            v >>= 5
    return out.getvalue()


def decode(s):
    out = StringIO.StringIO()
    while s:
        ins = (s[:8] + '0' * 7)[:8]
        s = s[8:]
        ins = [x for x in ins]
        ins.reverse()
        v = 0L
        for c in ins:
            if c not in de_alpha:
                raise RuntimeError, 'invalid character'
            v <<= 5
            v |= de_alpha[c]
        for i in range(5):
            out.write(chr(v & 0xFF))
            v >>= 8
    return out.getvalue()


if __name__ == '__main__':
    import sys
    import getopt
    import os
    import hashlib


    WIDTH = 87
    HEIGHT = 65

    BUF_SIZE = 1000 # Must be divisible by 5


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
        sys.stdout.write('# length: %s, alphabet: %s\n# md5: %s, sha1: %s\n' % (inp_len, alpha, h1.hexdigest(), h2.hexdigest()))


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
        optlist, args = getopt.getopt(sys.argv[1:], 'd:')

        do_decode = False
        decode_len = 0
        for opt, arg in optlist:
            if opt == '-d':
                decode_len = int(arg)
                do_decode = True

        if do_decode:
            dec_main(decode_len)
        else:
            enc_main()

    try:
        main()
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
