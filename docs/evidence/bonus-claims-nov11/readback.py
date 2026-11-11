from pathlib import Path
import urllib.request, hashlib, json, tarfile, xml.etree.ElementTree as ET, subprocess, datetime, re
root=Path.cwd(); out=root/'docs/evidence/bonus-claims-nov11'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat()
def get(url, cap=8_000_000):
 req=urllib.request.Request(url,headers={'User-Agent':'SilentShift-read-only-verification/1.0'})
 with urllib.request.urlopen(req, timeout=60) as r:
  data=r.read(cap+1)
  if len(data)>cap: raise ValueError('response exceeds read bound')
  return {'url':url,'http_status':r.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':r.headers.get('Content-Type')},data
raw='https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4'
v,b=get(raw); local=root/'evidence/video/silentshift-demo.mp4'; v['matches_local']=b==local.read_bytes(); assert v['matches_local']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(local)]))
v['media']={'duration_seconds':float(probe['format']['duration']),'streams':[{k:s[k] for k in ['codec_type','codec_name','width','height'] if k in s} for s in probe['streams']]}
v['release_asset_uploaded']=False; v['proposed_release_asset_url']='https://github.com/himanshu748/silentshift/releases/download/v0.3.1/silentshift-demo.mp4'
v['scope']='Anonymous full raw-file download now; release asset upload and its anonymous check are pending owner approval.'
(out/'video.json').write_text(json.dumps({'checked_at_ist':now,**v},indent=2)+'\n')
url='https://pm.community.intersystems.com/download/silentshift/-/silentshift-0.3.1.tgz'
with urllib.request.urlopen(url,timeout=60) as r:
 status=r.status
 with tarfile.open(fileobj=r,mode='r|gz') as tar:
  for member in tar:
   if member.name.lstrip('./')=='module.xml':
    assert member.size<1_000_000
    manifest=tar.extractfile(member).read(); break
  else: raise ValueError('manifest not found')
e=ET.fromstring(manifest); version=e.findtext('.//Module/Version'); assert version=='0.3.1'
(out/'public.json').write_text(json.dumps({'checked_at_ist':now,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'registry':{'url':url,'http_status':status,'manifest_version':version,'manifest_sha256':hashlib.sha256(manifest).hexdigest(),'scope':'Streamed manifest inspection only; no new registry install or native test.'},'release':json.loads((root/'.local/bonus-review/release.json').read_text()),'issue17':json.loads((root/'.local/bonus-review/issue17.json').read_text()),'articles':[]},indent=2)+'\n')
pub=json.loads((out/'public.json').read_text())
for url in ['https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production','https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery']:
 receipt,body=get(url); receipt['has_oex_link']='https://openexchange.intersystems.com/package/SilentShift' in body.decode(); pub['articles'].append(receipt)
receipt,body=get('https://openexchange.intersystems.com/package/SilentShift'); html=body.decode(); receipt['dedicated_idea_section']='Ideas to the app' in html; receipt['dpi_i_689_link']='https://ideas.intersystems.com/ideas/DPI-I-689' in html; receipt['note']='Public release 0.3.1; body retains 0.3.0 wording. No listing edit performed.'; pub['oex']=receipt
(out/'public.json').write_text(json.dumps(pub,indent=2)+'\n')
old=json.loads((root/'docs/evidence/voting-finish-nov10/candidate-031-source-identity.json').read_text())
files=[]
for path in ['src/SilentShift/Bridge.cls','src/SilentShift/Process/Semantic.cls','python/silentshift/engine.py']:
 data=(root/path).read_bytes(); h=hashlib.sha256(data).hexdigest(); prior=next(x for x in old['files'] if x['path']==path); assert h==prior['sha256']
 files.append({'path':path,'sha256':h,'matches_historical_live_gate':prior['matches_live_gate']})
(out/'embedded-python.json').write_text(json.dumps({'checked_at_ist':now,'source_commit':pub['source_commit'],'runtime_scope':'2026.3.0AI.154.0 / 154U ARM64 only','files':files,'language_declarations':['SilentShift.Bridge.Assess [ Language = python ]','SilentShift.Bridge.Policy [ Language = python ]'],'production_calls':['SilentShift.Process.Semantic.AssessCase calls SilentShift.Bridge.Assess','SilentShift.Process.Semantic.EvaluatePolicy calls SilentShift.Bridge.Policy'],'historical_execution_receipt':'docs/evidence/voting-finish-nov10/fresh-live-five.json','source_identity_receipt':'docs/evidence/voting-finish-nov10/candidate-031-source-identity.json','new_native_run':False,'technical_disqualification_found':False,'previous_not_claimed_reason':'Owner November 5 scope instruction, superseded by November 11 explicit instruction to claim proved Embedded Python usage. Separate unisolated signal-11 bug is not claimed.','organizer_qualification':'unconfirmed'},indent=2)+'\n')
print(json.dumps({'checked_at_ist':now,'video':v,'ipm_manifest':version,'article_checks':pub['articles'],'oex':pub['oex'],'embedded_source_matches':True},indent=2))
