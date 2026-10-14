"""Read SWG client .toc index files: map file path -> (tre name, offset, length, compressed length, compressor)."""
import struct, sys

def read_toc(path):
    d = open(path, 'rb').read()
    tag, ver, comp, _u1, _u2, nfiles, toc_size, nameblk, nameblk_unc, ntrees, treeblk = struct.unpack_from('<4s4sBBHIIIIII', d, 0)
    assert tag == b' COT', tag
    assert comp == 0, "compressed TOC not supported"
    pos = 36
    trees = d[pos:pos+treeblk].split(b'\0')[:ntrees]; pos += treeblk
    entries = []
    for i in range(nfiles):
        # name_len is the file name's length; names are stored back to back in entry order
        c, _, tree, _crc, name_len, off, length, clen = struct.unpack_from('<BBHIIIII', d, pos + i*24)
        entries.append((c, tree, name_len, off, length, clen))
    pos += toc_size
    names = d[pos:pos+nameblk_unc]
    out = {}
    name_off = 0
    for c, tree, name_len, off, length, clen in entries:
        out[names[name_off:name_off+name_len].decode('latin-1')] = (trees[tree].decode(), off, length, clen, c)
        name_off += name_len + 1
    return out

def read_all(paths):
    """Later (higher priority) TOCs override earlier ones."""
    merged = {}
    for p in paths:
        merged.update(read_toc(p))
    return merged

if __name__ == '__main__':
    m = read_all(sys.argv[1:])
    print(len(m), 'files')
