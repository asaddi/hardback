import cStringIO as StringIO


__all__ = ['ALPHA', 'encode', 'decode']


ALPHA = '0123456789ACDEFGHJKLMNPRSTUVWXYZ'
DE_ALPHA = {}
for i in range(len(ALPHA)):
    DE_ALPHA[ALPHA[i]] = i


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
            out.write(ALPHA[v & 0x1F])
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
            if c not in DE_ALPHA:
                raise RuntimeError, 'invalid character'
            v <<= 5
            v |= DE_ALPHA[c]
        for i in range(5):
            out.write(chr(v & 0xFF))
            v >>= 8
    return out.getvalue()
