"""Extract files from SWG .tre archives using the client's .toc index, and follow asset references."""
import os, re, sys, zlib
sys.path.insert(0, os.path.dirname(__file__))
import toc

TOCS = ['sku0_client.toc', 'sku1_client.toc', 'sku2_client.toc', 'sku3_client.toc']
REF = re.compile(rb'((?:appearance|shader|texture|effect|clientdata|object)/[A-Za-z0-9_/\.\-]+\.[a-z]{3})')

def load_index(client_dir):
    return toc.read_all([os.path.join(client_dir, t) for t in TOCS])

def read_file(index, tre_dir, name):
    tre, off, length, clen, comp = index[name]
    with open(os.path.join(tre_dir, tre), 'rb') as f:
        f.seek(off)
        raw = f.read(clen if comp else length)
    data = zlib.decompress(raw) if comp == 2 else raw
    assert len(data) == length, (name, len(data), length)
    return data

def refs(data):
    return sorted({m.decode() for m in REF.findall(data)})
