from pathlib import Path
import json,sys,subprocess,time,datetime
ROOT=Path.cwd(); C=ROOT/'.local/ship-030/fresh-clone'; OUT=ROOT/'.local/ship-030'
sys.path.insert(0,str(C/'scripts'));sys.path.insert(0,str(C/'python'))
from bootstrap import read_env
from verify_native import Client
v=read_env(C/'.env'); client=Client('http://127.0.0.1:52943/silentshift/api',v['SILENTSHIFT_VIEWER_USERNAME'],v['SILENTSHIFT_VIEWER_PASSWORD'])
sample=OUT/'csv-public-sample'
# Reuse the originals generated for the first preview; no import occurred.
body={k:(sample/f).read_bytes().decode() for k,f in [('orders_csv','orders.csv'),('approved_csv','approved.csv')]}
started=time.monotonic();status,data=client.call('/imports/csv/preview',body)
lines=body['orders_csv'].splitlines(); bad={**body,'orders_csv':lines[0]+'\n'+(lines[1]+'\n')*21}
rejected,rejection=client.call('/imports/csv/preview',bad)
receipt={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'public IPM 0.3.0 native preview API; read-only, no imports or inference; not a browser run','http_status':status,'preview':data,'bounded_rejection':{'rows_submitted':21,'http_status':rejected},'elapsed_seconds':round(time.monotonic()-started,3),'passed':status==200 and len(data.get('records',[]))==2 and data.get('mode')=='per-line-simulator' and rejected==422}
(OUT/'public-csv-preview.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='preview'}))
raise SystemExit(0 if receipt['passed'] else 1)
