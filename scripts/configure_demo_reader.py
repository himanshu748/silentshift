#!/usr/bin/env python3
"""Create a dedicated read-only demo principal in one named local container.

Operator-only deployment configuration, excluded from the native package. The
reader has no SSViewer/SSReviewer/SSImporter role. A scoped REST application role
adds read access and the existing Embedded Python read/serialization capability,
never database write. The private fixed-scenario runner is a different user.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def read_env(path):
    return dict(line.split('=', 1) for line in path.read_text().splitlines() if line and not line.startswith('#'))


def literal(value):
    return '"' + value.replace('"', '""') + '"'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--container',required=True)
    p.add_argument('--context')
    p.add_argument('--env-file',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    if not re.fullmatch(r'silentshift-(?:bonus-load-[a-z0-9-]+|demo-native)',a.container):
        raise ValueError('Use an explicitly named disposable SilentShift demo instance')
    env=read_env(a.env_file); user=env.get('DEMO_READER',''); password=env.get('DEMO_READER_PASSWORD','')
    if not re.fullmatch(r'ss-demo-reader(?:-[a-z0-9-]{1,20})?',user) or len(password)<16 or not re.fullmatch(r'[A-Za-z0-9_-]+',password):
        raise ValueError('Dedicated reader name and private single-line password required')
    plan={'container':a.container,'user':user,'roles':['SSDemoReader'],
          'database_access':'SILENTSHIFT read only','sql_grant':'SELECT Ens.MessageHeader and SilentShift_Data schema only',
          'review_import_or_production_control_granted':False,'executed':False}
    if not a.execute:
        print(json.dumps(plan));return
    docker=['docker']+(['--context',a.context] if a.context else [])
    def session(namespace,script):
        run=subprocess.run(docker+['exec','-i',a.container,'iris','session','IRIS','-U',namespace],
                           input=script+'\nhalt\n',capture_output=True,text=True,timeout=60)
        text=(run.stdout+run.stderr).replace(password,'<redacted>')
        log=a.env_file.with_suffix('.reader-setup.log')
        with log.open('a') as f:f.write(text)
        log.chmod(0o600)
        if run.returncode or 'SS_DEMO_READER_OK=1' not in text:
            raise RuntimeError('Reader configuration did not complete; private redacted log retained')
    code='''
set roles("SSDemoReader")="SSView:U,%DB_SILENTSHIFT:R,%Ens_Portal:U,%Ens_MessageTrace:U,%Ens_MessageContent:U"
set roles("SSDemoReadAPI")="%DB_SILENTSHIFT:R,%Service_EmbeddedPython:U"
set role=""
set role="SSDemoReader"
kill props set props("Resources")=roles(role),props("GrantedRoles")=""
if ##class(Security.Roles).Exists(role) { set sc=##class(Security.Roles).Modify(role,.props) } else { set sc=##class(Security.Roles).Create(role,"Synthetic demo read access",roles(role),"") }
if $system.Status.IsError(sc) { do $system.Status.DisplayError(sc) halt }
set role="SSDemoReadAPI"
kill props set props("Resources")=roles(role),props("GrantedRoles")=""
if ##class(Security.Roles).Exists(role) { set sc=##class(Security.Roles).Modify(role,.props) } else { set sc=##class(Security.Roles).Create(role,"Synthetic demo read access",roles(role),"") }
if $system.Status.IsError(sc) { do $system.Status.DisplayError(sc) halt }
set sc=##class(Security.Applications).Get("/silentshift",.app)
if $system.Status.IsError(sc) halt
set match=$get(app("MatchRoles"))
if match'["SSDemoReader:SSDemoReadAPI" set match=match_$select(match="":"",1:",")_"SSDemoReader:SSDemoReadAPI"
kill props set props("MatchRoles")=match
set sc=##class(Security.Applications).Modify("/silentshift",.props)
if $system.Status.IsError(sc) halt
set username=USER_LITERAL
if ##class(Security.Users).Exists(username) { set sc=##class(Security.Users).Get(username,.current) if $get(current("Roles"))'="SSDemoReader" halt }
kill props set props("Roles")="SSDemoReader",props("Password")=PASSWORD_LITERAL,props("NameSpace")="SILENTSHIFT",props("Enabled")=1,props("ChangePassword")=0
if ##class(Security.Users).Exists(username) { set sc=##class(Security.Users).Modify(username,.props) } else { set sc=##class(Security.Users).Create(username,.props) }
if $system.Status.IsError(sc) { do $system.Status.DisplayError(sc) halt }
write "SS_DEMO_READER_OK=1",!
'''.replace('USER_LITERAL',literal(user)).replace('PASSWORD_LITERAL',literal(password))
    session('%SYS',code)
    session('SILENTSHIFT','''set result=##class(%SQL.Statement).%ExecDirect(,"GRANT SELECT ON SCHEMA SilentShift_Data TO SSDemoReadAPI")
if result.%SQLCODE<0 { write "SQL read grant failed",! halt }
set result=##class(%SQL.Statement).%ExecDirect(,"GRANT SELECT ON Ens.MessageHeader TO SSDemoReader")
if result.%SQLCODE<0 { write "SQL grant failed",! halt }
write "SS_DEMO_READER_OK=1",!
''')
    plan['executed']=True;print(json.dumps(plan))


if __name__=='__main__':main()
