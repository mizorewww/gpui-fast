#!/usr/bin/env python3
"""Per-patch manifest edits in the Fast source layout. argv[1]=patch name."""
import sys,re
p=sys.argv[1]
def sub(f,a,b,count=1):
    s=open(f).read()
    assert a in s,(f,a)
    open(f,'w').write(s.replace(a,b,count))
if p=='14a-frame-observation-core':
    sub('crates/gpui/Cargo.toml','[features]\n','[features]\n# Material dev overlay: frame statistics, vsync control, CPU scopes. Off for consumers.\nframe-observation = []\n')
if p=='14b-frame-observation-apple':
    sub('crates/gpui_apple/Cargo.toml','[features]\n','[features]\nframe-observation = ["gpui/frame-observation"]\n')
if p=='14f-frame-observation-web':
    sub('crates/gpui_web/Cargo.toml','[features]\n','[features]\nframe-observation = ["gpui/frame-observation"]\n')
if p=='14c-frame-observation-macos':
    sub('crates/gpui_macos/Cargo.toml','[dependencies]\ngpui.workspace = true','[dependencies]\ngpui = { workspace = true, features = ["frame-observation"] }')
    s=open('crates/gpui_macos/Cargo.toml').read()
    s=re.sub(r'gpui_apple\.workspace = true','gpui_apple = { workspace = true, features = ["frame-observation"] }',s,count=1)
    assert 'gpui_apple = { workspace' in s
    open('crates/gpui_macos/Cargo.toml','w').write(s)
if p=='14d-frame-observation-linux-wgpu':
    sub('crates/gpui_linux/Cargo.toml',"gpui.workspace = true",'gpui = { workspace = true, features = ["frame-observation"] }')
if p=='14e-frame-observation-windows':
    sub('crates/gpui_windows/Cargo.toml','[dependencies]\ngpui.workspace = true','[dependencies]\ngpui = { workspace = true, features = ["frame-observation"] }')
