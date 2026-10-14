import os, sys
sys.path.insert(0, os.path.dirname(__file__)); import extract
idx = extract.load_index('.')
todo = list(sys.argv[1:]); seen = set(); need = {}; tree = {}
while todo:
    n = todo.pop()
    if n in seen or n not in idx: continue
    seen.add(n)
    tre = idx[n][0]
    if not os.path.exists(tre):
        need.setdefault(tre, []).append(n); continue
    rs = [r for r in extract.refs(extract.read_file(idx, '.', n)) if r.startswith(('appearance/', 'shader/', 'texture/')) and r != n]
    tree[n] = rs
    todo += rs
for k, v in tree.items(): print(k, '->', v)
print('need TREs:', need)
