"""Install PRK AOU without changing the regular AO client or renderer binaries."""
import argparse
import ctypes
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
LAYOUTS=('PRK_AOU_CYT','PRK_AOU_Slim_CNI','PRK_AOU_Slim_CNT')
NATIVE=('OptionPanel/Root.xml','OptionPanel/HotKeys.xml','Views/Skills.xml')
GUI_VALUE=re.compile(rb'<Value\b(?=[^>]*\bname\s*=\s*[\"\x27]GUIName[\"\x27])[^>]*/>')


def digest(data):return hashlib.sha256(data).hexdigest()


def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.prk-aou-staging');created=False
    try:
        with temporary.open('xb') as stream:
            created=True;stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if created and temporary.exists():temporary.unlink()


def save(path,value):atomic(path,(json.dumps(value,indent=2)+'\n').encode())


def parse_gui_xml(data,client_skills=False):
    try:return ET.fromstring(data)
    except ET.ParseError:
        if not client_skills:raise
        # The shipped PRK Skills view permits raw HTML in quoted TextView values.
        # Validate an escaped parser view, but deploy the original native bytes.
        converted=re.sub(rb'(\bvalue=")([^"]*)(")',lambda m:m[1]+m[2].replace(b'<',b'&lt;').replace(b'>',b'&gt;')+m[3],data,flags=re.S)
        if converted==data:raise
        return ET.fromstring(converted)


def client_closed(game):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_uint,ctypes.c_bool,ctypes.c_uint];kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    kernel.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint)]
    kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint)]
    count=1024
    while True:
        processes=(ctypes.c_uint*count)();returned=ctypes.c_uint()
        if not psapi.EnumProcesses(processes,ctypes.sizeof(processes),ctypes.byref(returned)):raise ctypes.WinError()
        if returned.value<ctypes.sizeof(processes):break
        count*=2
    target=game/'AnarchyOnline.exe'
    for pid in processes[:returned.value//4]:
        handle=kernel.OpenProcess(0x1000,False,pid)
        if not handle:continue
        try:
            code=ctypes.c_uint();name=ctypes.create_unicode_buffer(32768);size=ctypes.c_uint(len(name))
            if kernel.GetExitCodeProcess(handle,ctypes.byref(code)) and code.value==259 and kernel.QueryFullProcessImageNameW(handle,0,name,ctypes.byref(size)):
                if Path(name.value)==target:raise ValueError('Exit Project Rubi-Ka normally before changing its GUI files')
        finally:kernel.CloseHandle(handle)


def gui_name(data):
    nodes=[v for v in ET.fromstring(data).iter('Value') if v.get('name')=='GUIName']
    if len(nodes)>1:raise ValueError('Duplicate GUIName preference')
    return nodes[0].get('value') if nodes else None


def set_gui_name(data,value):
    if len(GUI_VALUE.findall(data))>1:raise ValueError('Duplicate GUIName preference')
    replacement=b'' if value is None else ('<Value name="GUIName" value="'+html.escape(value,quote=True)+'" />').encode()
    if GUI_VALUE.search(data):changed=GUI_VALUE.sub(lambda _:replacement,data)
    elif value is not None:
        at=data.rfind(b'</Root>')
        if at<0:raise ValueError('Unrecognized preference XML root')
        changed=data[:at]+b'    '+replacement+b'\n'+data[at:]
    else:changed=data
    ET.fromstring(changed);return changed


def inspect(game,profile,layout):
    if not (game/'AnarchyOnline.exe').is_file() or not (game.parent/'PRK.Launcher.exe').is_file():
        raise ValueError('GamePath must be the Project Rubi-Ka launcher client subdirectory')
    version=(game/'version.id').read_text().strip()
    if version!='00.7.2_EP1':raise ValueError('This GUI port has only been validated against PRK 00.7.2_EP1')
    default=game/'cd_image/gui/Default'
    plan={}
    for file in (ROOT/'Gui').rglob('*'):
        if file.is_file():plan[profile/'Gui'/file.relative_to(ROOT/'Gui')]=file.read_bytes()
    for name in LAYOUTS:
        for relative in NATIVE:plan[profile/'Gui'/name/relative]=(default/relative).read_bytes()
    for file in (ROOT/'scripts').rglob('*'):
        if file.is_file():
            data=file.read_bytes();relative=file.relative_to(ROOT/'scripts')
            plan[profile/'scripts'/relative]=data
            # /showfile resolves against the install root, not only AppData.
            plan[game/'scripts'/relative]=data
    for path,data in plan.items():
        if path.suffix.lower()=='.xml':parse_gui_xml(data,path.name=='Skills.xml')
    prefs=profile/'Prefs/Prefs.xml';original=prefs.read_bytes();before=gui_name(original)
    plan[prefs]=set_gui_name(original,'"'+layout+'"')
    # Native category names and value/type bindings are copied without reinterpretation.
    baseline=ET.fromstring((default/'OptionPanel/Root.xml').read_bytes())
    bindings=[dict(v.attrib) for v in baseline.iter() if v.get('opt_variable')]
    return plan,prefs,before,{'client_version':version,'native_settings_bindings':len(bindings),'xml_files':sum(p.suffix.lower()=='.xml' for p in plan)}


def install(args):
    game=args.game.resolve();profile=args.profile.resolve();state=args.state.resolve()
    if state.is_relative_to(ROOT):raise ValueError('State must be outside the source repository')
    plan,prefs,before,report=inspect(game,profile,args.layout)
    if args.dry_run:
        print(json.dumps({'status':'prepared','files':len(plan),'layout':args.layout,**report}));return
    client_closed(game)
    marker=state/'installed.json'
    if marker.exists():
        previous=json.loads(marker.read_text())
        if previous['game']!=str(game) or previous['profile']!=str(profile) or previous['layout']!=args.layout:
            raise ValueError('State belongs to a different installation/layout; uninstall it first')
        for row in previous['files']:
            if row['path']==str(prefs):continue
            path=Path(row['path'])
            if not path.is_file() or digest(path.read_bytes())!=row['after']:
                raise ValueError('Installed file changed; preserve it and remove optional armor integration before GUI reinstall')
        print(json.dumps({'status':'already-installed','layout':args.layout,**report}));return
    state.mkdir(parents=True,exist_ok=True);records=[]
    for path,data in plan.items():
        original=path.read_bytes() if path.exists() else None
        backup=None
        if original is not None:
            backup='backups/'+digest(str(path).encode())+'.original'
            stored=state/backup
            if stored.exists() and stored.read_bytes()!=original:raise ValueError('Existing checkpoint differs from this installation')
            if not stored.exists():atomic(stored,original)
        records.append({'path':str(path),'before':None if original is None else digest(original),'backup':backup,'after':digest(data)})
    journal={'schema':1,'status':'installing','game':str(game),'profile':str(profile),'layout':args.layout,'prefs':str(prefs),'previous_gui_name':before,'files':records,'verification':report}
    save(marker,journal)
    try:
        for row in records:
            path=Path(row['path']);actual=path.read_bytes() if path.exists() else None
            if (None if actual is None else digest(actual))!=row['before']:raise ValueError('A destination changed after planning; refusing overwrite')
            atomic(path,plan[path])
        for row in records:
            if digest(Path(row['path']).read_bytes())!=row['after']:raise ValueError('Installed file hash mismatch')
        journal['status']='installed';save(marker,journal)
    except BaseException:
        restore(journal,state,failed_install=True)
        raise
    print(json.dumps({'status':'installed','layout':args.layout,'files':len(records),**report}))


def restore(journal,state,failed_install=False):
    prefs=Path(journal['prefs']);owned=[]
    for row in journal['files']:
        path=Path(row['path'])
        if path==prefs and not failed_install:continue
        actual=path.read_bytes() if path.exists() else None;value=None if actual is None else digest(actual)
        if value not in (row['before'],row['after']):raise ValueError('A file was changed outside this installer; refusing restore: '+path.name)
        if value==row['after']:owned.append(row)
        if row['backup'] and digest((state/row['backup']).read_bytes())!=row['before']:raise ValueError('Backup hash mismatch')
    for row in reversed(owned):
        path=Path(row['path'])
        if row['backup']:atomic(path,(state/row['backup']).read_bytes())
        else:path.unlink()
    if not failed_install:
        current=prefs.read_bytes()
        if gui_name(current)=='"'+journal['layout']+'"':atomic(prefs,set_gui_name(current,journal['previous_gui_name']))
    (state/'installed.json').unlink()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['install','uninstall']);p.add_argument('--game',type=Path);p.add_argument('--profile',type=Path);p.add_argument('--state',type=Path,required=True);p.add_argument('--layout',choices=LAYOUTS,default=LAYOUTS[0]);p.add_argument('--dry-run',action='store_true');args=p.parse_args()
    if args.action=='install':
        if not args.game or not args.profile:p.error('install requires game and profile paths')
        install(args)
    else:
        journal=json.loads((args.state/'installed.json').read_text());client_closed(Path(journal['game']));restore(journal,args.state);print('PRK GUI removed; unrelated preference settings preserved. Private backups retained.')


if __name__=='__main__':main()
