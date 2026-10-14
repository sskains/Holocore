"""Parse ImageStyle definitions (with their namespace path) out of SWG ui/*.inc text."""
import re
TAG = re.compile(r"<(/?)(Namespace|ImageStyle)\b([^>]*?)(/?)>", re.S)
ATTR = re.compile(r"(\w+)='([^']*)'")

def image_styles(text):
    stack, out = [], []
    for m in TAG.finditer(text):
        closing, tag, attrs, selfclose = m.groups()
        if tag == 'Namespace':
            if closing: stack.pop()
            else:
                a = dict(ATTR.findall(attrs)); stack.append(a.get('Name', '?'))
                if selfclose: stack.pop()
        elif not closing:
            a = dict(ATTR.findall(attrs))
            out.append({'path': '.'.join(stack + [a.get('Name', '?')]), 'name': a.get('Name', ''),
                        'source': a.get('Source', ''), 'rect': a.get('SourceRect', ''),
                        'start': m.start(), 'end': m.end()})
    return out
