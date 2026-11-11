const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require(path.resolve(__dirname,'../web/node_modules/playwright'));
const root=path.resolve(__dirname,'../docs/site'),output=path.resolve(process.argv[2]||'.local/evidence-tour-browser');
(async()=>{
 await fs.mkdir(output,{recursive:true});const server=http.createServer(async(req,res)=>{
  try{const p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));if(p!==root&&!p.startsWith(root+path.sep))throw Error('outside root');const file=await fs.stat(p);const target=file.isDirectory()?path.join(p,'index.html'):p;const data=await fs.readFile(target);res.writeHead(200,{'Content-Type':{'.html':'text/html','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.woff2':'font/woff2','.png':'image/png','.webp':'image/webp'}[path.extname(target)]||'application/octet-stream'});res.end(data);
  }catch{res.writeHead(404);res.end('Not found');}
 });await new Promise(r=>server.listen(0,'127.0.0.1',r));const base='http://127.0.0.1:'+server.address().port;let browser;const checks=[],errors=[],requests=[];const check=(n,v)=>{assert.ok(v,n);checks.push(n);};
 try{
  browser=await chromium.launch(process.env.SILENTSHIFT_CHROME_CHANNEL?{channel:process.env.SILENTSHIFT_CHROME_CHANNEL}:{});
  for(const width of [1440,375]){
   const context=await browser.newContext({viewport:{width,height:960},reducedMotion:'reduce'});const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
   await page.goto(base+'/');
   check(width+': accurate recorded CTA is primary',await page.getByRole('link',{name:'Explore recorded cases'}).getAttribute('href')==='evidence-tour.html');
   await page.getByRole('link',{name:'Explore recorded cases'}).click();await page.waitForFunction(()=>document.querySelector('#recorded-route').textContent==='QUARANTINED');
   check(width+': starts with historical held case',(await page.locator('#recorded-id').innerText()).startsWith('EF61BAE2-'));
   check(width+': synthetic/recorded limit visible',(await page.locator('body').innerText()).includes('no new investigation'));
   check(width+': no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.getByRole('tab',{name:'03 Decision'}).click();
   check(width+': wrong ALLOW proposal is retained',(await page.locator('#step-title').innerText()).includes('Policy refused'));
   check(width+': final route stays quarantined',await page.locator('#recorded-route').innerText()==='QUARANTINED');
   check(width+': failed policy gates shown',await page.locator('.tour-check[data-passed="false"]').count()>0);
   await page.screenshot({path:path.join(output,'tour-held-'+width+'.png'),fullPage:true});
   await page.getByRole('tab',{name:'04 Receipt'}).click();await page.waitForFunction(()=>document.querySelector('.tour-signature').textContent.includes('signature is valid'));
   check(width+': real held-case signature verifies',(await page.locator('.tour-signature').innerText()).includes('Independent signing identity is not established'));
   await page.getByRole('link',{name:'Try an edited copy'}).click();await page.waitForFunction(()=>document.querySelector('#verification').dataset.state==='valid');
   check(width+': inspector retains chosen case',(await page.locator('#case-id').innerText()).startsWith('EF61BAE2-'));
   await page.getByRole('button',{name:'Test an edited copy'}).click();await page.waitForFunction(()=>document.querySelector('#signature-check').textContent==='Invalid');
   check(width+': chosen case tamper is detected',await page.locator('#verification').getAttribute('data-state')==='invalid');
   await page.goto(base+'/evidence-tour.html?case=approved-amendment&step=1');await page.waitForFunction(()=>document.querySelector('#recorded-route').textContent==='DELIVERED');
   check(width+': direct approved link selects correct case',(await page.locator('#recorded-id').innerText()).startsWith('1EEE38DB-'));
   check(width+': original amendment is visible',(await page.locator('#step-body').innerText()).includes('contract:PO-2048:v2'));
   await page.reload();await page.waitForFunction(()=>document.querySelector('#step-title').textContent.includes('amendment'));
   check(width+': refresh preserves step',await page.getByRole('tab',{name:'02 Authority'}).getAttribute('aria-selected')==='true');
   await page.getByRole('tab',{name:'02 Authority'}).focus();await page.keyboard.press('ArrowRight');
   check(width+': keyboard selects decision tab',await page.getByRole('tab',{name:'03 Decision'}).getAttribute('aria-selected')==='true');
   await page.getByRole('button',{name:'Next: receipt'}).click();await page.waitForFunction(()=>document.querySelector('.tour-signature').textContent.includes('signature is valid'));
   check(width+': step navigation focuses panel',await page.locator('#step-panel').evaluate(e=>e===document.activeElement));
   check(width+': recorded delivered count retained',(await page.locator('#recorded-effect').innerText()).endsWith('1'));
   await page.screenshot({path:path.join(output,'tour-approved-'+width+'.png'),fullPage:true});
   await page.getByRole('button',{name:'Unsupported change'}).click();await page.waitForFunction(()=>document.querySelector('#recorded-route').textContent==='QUARANTINED');
   check(width+': case switch preserves selected step',await page.getByRole('tab',{name:'04 Receipt'}).getAttribute('aria-selected')==='true');
   check(width+': baseline limitation remains visible',(await page.locator('body').innerText()).includes('did not establish better overall'));
   await context.close();
  }
  const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();await page.goto(base+'/evidence-tour.html');check('No-script raw evidence remains available',await page.locator('noscript').isVisible());await context.close();
  check('No console/page exceptions',errors.length===0);check('Only local GET requests',requests.every(r=>r.method==='GET'&&r.url.startsWith(base+'/')));
  console.log(JSON.stringify({passed:true,checks:checks.length,output}));
 }catch(e){errors.push(String(e));console.error(e);process.exitCode=1;}
 finally{await browser?.close();await new Promise(r=>server.close(r));await fs.writeFile(path.join(output,'browser.json'),JSON.stringify({checked_at:new Date().toISOString(),scope:'Local static recorded evidence tour, not a native or hosted run',passed:process.exitCode!==1,checks,errors,requests},null,2)+'\n');}
})();
