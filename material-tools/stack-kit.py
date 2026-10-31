#!/usr/bin/env python3
import re,os,subprocess,sys
W=os.path.expanduser('~/Developer/.figma-shots/work/forks')
text=open(f'{W}/diffs/gpui-base.diff',errors='replace').read()
FILES={'src/dialog.rs':'b1-dialog-accessible-name','src/input/base/element.rs':'b2-input-ime-anchor','src/input/base/state.rs':'b2-input-ime-anchor','src/lib.rs':'b3-motion-transition-playback','src/motion.rs':'b3-motion-transition-playback','src/toolbar.rs':'b5-toolbar-axis','src/slider.rs':'b4-slider-step-rtl-focus'}
out={}
for fd in re.split(r'(?m)^diff .*\n',text)[1:]:
    lines=fd.split('\n')
    rel=lines[1].split('\t')[0].split()[-1].split('vendor/gpui-base/',1)[1]
    if rel not in FILES: continue
    out.setdefault(FILES[rel],[]).append(f'--- a/crates/base/{rel}\n+++ b/crates/base/{rel}\n'+'\n'.join(lines[2:]))
os.makedirs(f'{W}/patches-kit',exist_ok=True)
for k,v in out.items(): open(f'{W}/patches-kit/{k}.diff','w').write(''.join(v))
print(sorted(out))
