import concurrent.futures, datetime, hashlib, html, json, pathlib, re, time, urllib.request
ROOT = pathlib.Path.cwd()
OUT = ROOT / 'docs/evidence/voting-week-nov10'
OUT.mkdir(parents=True, exist_ok=True)
URLS = {
 'listing': 'https://openexchange.intersystems.com/package/SilentShift',
 'contest': 'https://openexchange.intersystems.com/contest/49',
 'overview': 'https://community.intersystems.com/post/catching-semantic-failures-iris-interoperability-production',
 'review': 'https://community.intersystems.com/post/recoverable-human-review-iris-approval-one-delivery',
 'youtube_oembed': 'https://www.youtube.com/oembed?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3Da4dOcqu89EA&format=json',
 'mp4': 'https://raw.githubusercontent.com/himanshu748/silentshift/main/evidence/video/silentshift-demo.mp4',
}
def check(item):
 name,url=item
 row={'url':url,'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authentication':'none; no Cookie or Authorization headers'}
 t=time.monotonic()
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'SilentShift-read-only-verification/1.0'})
  with urllib.request.urlopen(req,timeout=45) as response:
   row.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
   if name=='mp4':
    digest=hashlib.sha256(); length=0
    while chunk:=response.read(1024*1024): digest.update(chunk); length+=len(chunk)
    row.update(bytes=length,sha256=digest.hexdigest(),complete_download=True)
    local=ROOT/'.local/voting-week/main/evidence/video/silentshift-demo.mp4'
    row['matches_fresh_main_file']=digest.hexdigest()==hashlib.sha256(local.read_bytes()).hexdigest()
   else:
    raw=response.read(); row.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    text=raw.decode('utf-8','replace')
    if name=='youtube_oembed': row['metadata']=json.loads(text)
    else:
     visible=html.unescape(re.sub('<[^>]+>',' ',text)); visible=re.sub(r'\s+',' ',visible)
     row['signals']={
      'has_idea_heading':'Ideas to the app' in visible,
      'has_dpi_link':'https://ideas.intersystems.com/ideas/DPI-I-689' in text,
      'has_archive_030':'silentshift-0.3.0.tgz' in text,
      'has_legacy_csv_sentence':'CSV is source-only' in visible,
      'has_legacy_native_020':'public native IPM 0.2.0' in visible,
      'has_youtube_link':'a4dOcqu89EA' in text,
      'has_mp4_link':'silentshift-demo.mp4' in text,
      'has_oex_backlink':'https://openexchange.intersystems.com/package/SilentShift' in text,
      'has_overview_link':'/post/catching-semantic-failures-iris-interoperability-production' in text,
      'has_review_link':'/post/recoverable-human-review-iris-approval-one-delivery' in text,
      'has_staff_video_feature':'We just featured your video' in visible,
     }
     if name=='contest': row['signals']['silentshift_registered']='href="/package/SilentShift"' in text or 'https://openexchange.intersystems.com/package/SilentShift' in text
 except Exception as exc: row['error']=str(exc)
 row['elapsed_seconds']=round(time.monotonic()-t,3)
 return name,row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=dict(pool.map(check,URLS.items()))
receipt={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Phase 0 anonymous link and media verification; no installation, inference, publication or external write','fresh_main':'a10de3f61e1d809b374832a4db67761318bc16ea','checks':results}
(OUT/'public-readback.json').write_text(json.dumps(receipt,indent=2)+'\n')
for name,row in results.items(): print(name,json.dumps(row))
