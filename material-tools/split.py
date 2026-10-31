#!/usr/bin/env python3
"""Split vendor-vs-archive diffs into per-patch diffs in the Fast source layout."""
import re,sys,os,collections
W=os.path.expanduser('~/Developer/.figma-shots/work/forks')
CR={'gpui-fast':'crates/gpui','gpui-fast-apple':'crates/gpui_apple','gpui-fast-web':'crates/gpui_web','gpui-fast-macos':'crates/gpui_macos','gpui-fast-wgpu':'crates/gpui_wgpu','gpui-fast-linux':'crates/gpui_linux','gpui-fast-windows':'crates/gpui_windows'}
DROP='DROP'
def classify(crate,f,t):
    # t = whole hunk text, changed = changed lines only
    ch='\n'.join(l for l in t.split('\n') if l[:1] in '+-')
    if f.endswith(('MATERIAL-MIGRATION.json','Cargo.lock')) or f=='Cargo.toml' or f.startswith('tests/fonts') or f.startswith('examples/image'): return DROP  # manifests written by hand below; fixtures are source-tree paths upstream
    if crate=='gpui-fast':
        if f=='src/tab_stop.rs': return '03-tab-stop-index'
        if f=='src/elements/animation.rs': return '04-animation-playback'
        if f=='src/elements/div.rs': return '09-wheel-scroll-no-move'
        if f in('src/svg_renderer.rs',): return DROP  # test path only meaningful in the published layout
        if f=='src/fast/layers/reuse.rs': return '16-warnings-toolchain'
        if f in('src/fast/dependencies.rs','src/fast/tests/dependencies.rs'): return '15-render-lease'
        if re.search(r'try_update',ch) and f.startswith('src/profiler') and 'frame-observation' not in ch: return '16-warnings-toolchain'
        if re.search(r'^\s*$', re.sub(r'^[+-]','',ch,flags=re.M)) : return DROP
        if 'swap_global_quietly' in ch: return '05-quiet-global-swap'
        if 'focused_input_selection_bounds' in ch: return '06-focused-input-bounds'
        if 'self.draw(cx).clear(cx)' in ch: return '11-touch-draws-before-dispatch'
        if f=='src/app.rs' and 'window_invalidators_by_entity' in ch: return '10-entity-set-diff'
        if 'hanging_space' in ch or 'test_wrap_line_hangs' in ch or f=='src/text_system/line_wrapper.rs' and 'Boundary::new' in ch: return '07-hanging-space'
        if f=='src/text_system.rs' and "glyph_for_char(font_id, 'm')" in ch: return '08-em-fallback'
        if re.search(r'letter_spacing|shape_text_spaced|layout_line_spaced|layout_wrapped_line_spaced|shaped_width_for_char',ch): return '02-letter-spacing'
        if re.search(r'layout_direction|LayoutDirection|mirrored|set_mirrored|in_direction|child_offset|flip_x|border_widths|\brtl\b|Rtl',ch): return '01-layout-direction'
        if f=='src/style.rs' and '#[test]' in ch: return DROP
        return '14a-frame-observation-core'
    if crate=='gpui-fast-apple':
        if f in('src/open_type.rs','src/text_system.rs','tests/font_fallback.rs'): return '13-apple-font-fallback'
        if f=='src/fast/rounded_clip_shader.rs': return '16-warnings-toolchain'
        return '14b-frame-observation-apple'
    if crate=='gpui-fast-web':
        if 'set_position' in ch or 'update_ime_position' in ch: return '12-web-ime-position'
        return '14f-frame-observation-web'
    if crate=='gpui-fast-macos': return '14c-frame-observation-macos'
    if crate=='gpui-fast-wgpu':
        if 'cfg(any())' in ch or 'rounded_clip_fixtures' in ch: return DROP
        return '14d-frame-observation-linux-wgpu'
    if crate=='gpui-fast-linux': return '14d-frame-observation-linux-wgpu'
    if crate=='gpui-fast-windows': return '14e-frame-observation-windows'
    raise SystemExit(crate)
out=collections.defaultdict(lambda:collections.OrderedDict())
stats=collections.Counter()
for crate,dest in CR.items():
    text=open(f'{W}/diffs/{crate}.diff',errors='replace').read()
    for fd in re.split(r'(?m)^diff .*\n',text)[1:]:
        lines=fd.split('\n')
        name=lines[1].split('\t')[0].split()[-1]
        rel=name.split(f'vendor/{crate}/',1)[1]
        hunks=re.split(r'(?m)^(?=@@ )','\n'.join(lines[2:]))
        new=lines[0].startswith('--- ') and '1970' in lines[0]
        for h in hunks:
            if not h.startswith('@@'):continue
            p=classify(crate,rel,h)
            if rel=='src/app.rs' and p=='01-layout-direction' and 'CpuFrameScope' in h: p='14a-frame-observation-core'
            n=sum(1 for l in h.split('\n') if l[:1] in '+-')
            # The release generator adds these headers; the source tree has none.
            h,k=re.subn(r'(?m)^ // Modified (by Longbridge for gpui-fast\.|for gpui-fast releases:.*)\n','',h)
            if k:
                m=re.match(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@',h)
                h=f'@@ -{m[1]},{int(m[2])-k} +{m[3]},{int(m[4])-k} @@'+h[m.end():]
            stats[p]+=n
            if p==DROP: continue
            out[p].setdefault(f'{dest}/{rel}',[]).append(h.rstrip('\n')+'\n')
os.makedirs(f'{W}/patches',exist_ok=True)
for p,files in sorted(out.items()):
    with open(f'{W}/patches/{p}.diff','w') as fh:
        for f,hs in files.items():
            isnew=hs[0].startswith('@@ -0,0')
            fh.write(f'--- {"/dev/null" if isnew else "a/"+f}\n+++ b/{f}\n'); fh.writelines(hs)
    print(p,stats[p],'lines',len(files),'files')
print(DROP,stats[DROP])
