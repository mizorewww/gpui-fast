#!/usr/bin/env python3
"""Simulate Fast's next Zed sync: 3-way merge each tracked file's zed A->B onto Fast HEAD.
Files where Fast itself conflicts keep Fast's side of that hunk (Fast's maintainers resolve those)."""
import subprocess as sp,os,re,sys,tempfile
W=os.path.expanduser('~/Developer/.figma-shots/work/forks')
A,B=sys.argv[1:3]
fast=f'{W}/gpui-fast';zed=f'{W}/zed'
tr=re.findall(r'"((?:crates|tooling)/[a-z_/]+)"',sp.check_output(['git','-C',fast,'show','origin/main:UPSTREAM'],text=True))
names=sp.check_output(['git','-C',zed,'diff','--name-status','--no-renames',A,B,'--']+tr,text=True).splitlines()
print(len(names),'zed files changed')
sp.check_call(['git','-C',fast,'checkout','-q','-f','--detach','origin/main'])
clean=confl=0;cf=[];hunks=0
for l in names:
    st,p=l.split('\t')
    full=f'{fast}/{p}'
    if st=='D':
        if os.path.exists(full): os.remove(full)
        continue
    blob=sp.check_output(['git','-C',zed,'show',f'{B}:{p}'])
    if st=='A' or not os.path.exists(full):
        os.makedirs(os.path.dirname(full),exist_ok=True); open(full,'wb').write(blob); continue
    with tempfile.TemporaryDirectory() as d:
        open(d+'/base','wb').write(sp.check_output(['git','-C',zed,'show',f'{A}:{p}']))
        open(d+'/theirs','wb').write(blob)
        r=sp.run(['git','merge-file','-p',full,d+'/base',d+'/theirs'],capture_output=True)
        if r.returncode==0: open(full,'wb').write(r.stdout); clean+=1
        else:
            hunks+=max(r.returncode,0);confl+=1;cf.append(f'{p}:{r.returncode}')
            r2=sp.run(['git','merge-file','-p','--ours',full,d+'/base',d+'/theirs'],capture_output=True)
            open(full,'wb').write(r2.stdout)
print('merged clean',clean,'Fast-side conflicts in',confl,'files,',hunks,'hunks');print(' '.join(cf))
sp.check_call(['git','-C',fast,'add','-A','crates','tooling'])
sp.check_call(['git','-C',fast,'-c','user.name=sim','-c','user.email=sim@local','commit','-q','-m','SIM: zed sync (not pushed)'])
print(sp.check_output(['git','-C',fast,'rev-parse','HEAD'],text=True).strip())
