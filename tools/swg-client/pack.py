"""Build an SWG .tre archive (version 5000) from a folder laid out like the client's file paths.

Usage: python pack.py <source_folder> <output.tre>
Every file under source_folder is stored as its relative path, e.g. texture/sabre_anakin.dds.
"""
import hashlib, os, struct, sys, zlib

def _table():
    t = []
    for i in range(256):
        c = i << 24
        for _ in range(8):
            c = ((c << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if c & 0x80000000 else (c << 1) & 0xFFFFFFFF
        t.append(c)
    return t
_T = _table()

def swg_crc(name: bytes) -> int:
    c = 0xFFFFFFFF
    for b in name:
        c = ((c << 8) & 0xFFFFFFFF) ^ _T[((c >> 24) ^ b) & 0xFF]
    return c ^ 0xFFFFFFFF

def pack(src, out):
    files = []
    for root, _, names in os.walk(src):
        for n in names:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, src).replace(os.sep, '/').lower()
            files.append((rel.encode(), open(full, 'rb').read()))
    files.sort(key=lambda f: swg_crc(f[0]))  # the client binary-searches the TOC by CRC

    body = bytearray(); entries = []; names = bytearray(); md5s = bytearray()
    header_size = 36
    for name, data in files:
        packed = zlib.compress(data, 9)
        use = packed if len(packed) < len(data) else data
        comp = 2 if use is packed else 0
        entries.append(struct.pack('<IIIIII', swg_crc(name), len(data), header_size + len(body), comp, len(use) if comp else 0, len(names)))
        body += use; names += name + b'\0'; md5s += hashlib.md5(data).digest()
    toc = zlib.compress(b''.join(entries), 9); nb = zlib.compress(bytes(names), 9)
    header = struct.pack('<4s4sIIIIIII', b'EERT', b'5000', len(files), header_size + len(body), 2, len(toc), 2, len(nb), len(names))
    with open(out, 'wb') as f:
        f.write(header); f.write(body); f.write(toc); f.write(nb); f.write(md5s)
    return [n.decode() for n, _ in files]

if __name__ == '__main__':
    for n in pack(sys.argv[1], sys.argv[2]):
        print('packed', n)
