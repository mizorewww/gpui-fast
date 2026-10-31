#!/usr/bin/env python3
"""List hunks of a recursive unified diff with a one-line gist."""
import sys,re
path=sys.argv[1]
cur=None;h=None;out=[]
def flush():
    global h
    if h:
        adds=[l[1:].strip() for l in h['b'] if l.startswith('+')]
        dels=[l[1:].strip() for l in h['b'] if l.startswith('-')]
        gist=' | '.join(x for x in (adds or dels) if x and not x.startswith('//'))[:int(sys.argv[2]) if len(sys.argv)>2 else 150]
        print(f"{cur} {h['hdr']} +{len(adds)}-{len(dels)}: {gist}")
    h=None
for l in open(path,errors='replace'):
    l=l.rstrip('\n')
    if l.startswith('diff '):
        flush();cur=l.split()[-1].split('/',1)[-1]
    elif l.startswith('@@'):
        flush();h={'hdr':l.split('@@')[1].strip().split()[1],'b':[]}
    elif h is not None and not l.startswith('+++') and not l.startswith('---'):
        h['b'].append(l)
flush()
