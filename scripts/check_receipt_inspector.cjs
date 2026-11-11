// Local static browser gate. No native API, model, deployment or file upload endpoint.
const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require(path.resolve(__dirname,'../web/node_modules/playwright'));
const root=path.resolve(__dirname,'../docs/site');
const output=path.resolve(process.argv[2]||'.local/receipt-inspector-browser');
(async()=>{
 await fs.mkdir(output,{recursive:true});
 const server=http.createServer(async(req,res)=>{
  try{const p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));if(!p.startsWith(root+path.sep))throw Error('outside root');
   const data=await fs.readFile(p);const type={'.html':'text/html','.css':'text/css','.mjs':'text/javascript','.json':'application/json','.woff2':'font/woff2','.png':'image/png'}[path.extname(p)]||'application/octet-stream';res.writeHead(200,{'Content-Type':type});res.end(data);
  }catch{res.writeHead(404);res.end('Not found');}
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const base='http://127.0.0.1:'+server.address().port;let browser;const checks=[],errors=[],network=[];
 const check=(name,condition)=>{assert.ok(condition,name);checks.push(name);};
 try{
  browser=await chromium.launch(process.env.SILENTSHIFT_CHROME_CHANNEL?{channel:process.env.SILENTSHIFT_CHROME_CHANNEL}:{});
  for(const width of [1440,375]){
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});const page=await context.newPage();
   page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>network.push({url:r.url(),method:r.method()}));
   await page.goto(base+'/receipts.html');await page.waitForFunction(()=>document.querySelector('#verification').dataset.state==='valid');
   check(width+': real export verifies',await page.locator('#signature-check').innerText()==='Valid');
   check(width+': native case identity retained',(await page.locator('#case-id').innerText()).startsWith('1EEE38DB-'));
   check(width+': scope is visible',(await page.locator('body').innerText()).includes('no IRIS connection'));
   check(width+': no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.screenshot({path:path.join(output,'receipt-'+width+'.png'),fullPage:true});
   await page.getByRole('button',{name:'Test an edited copy'}).click();
   await page.waitForFunction(()=>document.querySelector('#verification').dataset.state==='invalid');
   check(width+': action moves focus to result',await page.locator('#verification').evaluate(e=>e===document.activeElement));
   check(width+': changed outcome fails',await page.locator('#signature-check').innerText()==='Invalid');
   check(width+': editor now shows local REVIEW',(await page.locator('#receipt-text').inputValue()).includes('"decision": "REVIEW"'));
   await page.getByRole('button',{name:'Load recorded sample'}).click();await page.waitForFunction(()=>document.querySelector('#verification').dataset.state==='valid');
   await page.locator('#expected-key').fill('');
   check(width+': editing invalidates old success',await page.locator('#verification').getAttribute('data-state')==='unchecked');
   await page.getByRole('button',{name:'Verify receipt'}).click();await page.waitForFunction(()=>document.querySelector('#verification').dataset.state==='untrusted');
   check(width+': embedded key alone never claims identity',(await page.locator('#verification').innerText()).includes('identity is unverified'));
   await page.locator('#expected-key').fill('0'.repeat(64));await page.getByRole('button',{name:'Verify receipt'}).click();
   await page.waitForFunction(()=>document.querySelector('#identity-check').textContent==='Different key');
   check(width+': key substitution flagged',await page.locator('#verification').getAttribute('data-state')==='invalid');
   await page.locator('#receipt-text').fill('{"a":1,"a":2}');await page.getByRole('button',{name:'Verify receipt'}).click();
   await page.waitForFunction(()=>document.querySelector('#verification').textContent.includes('Duplicate JSON field'));
   check(width+': invalid input is announced',await page.locator('#verification').getAttribute('role')==='status');
   await page.locator('#receipt-file').setInputFiles({name:'oversized.json',mimeType:'application/json',buffer:Buffer.alloc(65537,32)});
   await page.waitForFunction(()=>document.querySelector('#verification').textContent.includes('64 KiB'));
   check(width+': bounded local file rejected',await page.locator('#receipt-details').isHidden());
   await page.locator('#receipt-file').setInputFiles({name:'sample.json',mimeType:'application/json',buffer:await fs.readFile(path.join(root,'assets/pex-sample.json'))});
   await page.waitForFunction(()=>document.querySelector('#verification').dataset.state==='untrusted');
   check(width+': local file has no trusted identity by default',await page.locator('#expected-key').inputValue()==='');
   await page.goto(base+'/receipts.html');await page.keyboard.press('Tab');
   check(width+': keyboard skip link is first',await page.locator('.skip-link').evaluate(e=>e===document.activeElement));
   await page.keyboard.press('Enter');
   check(width+': skip target exists',await page.locator('#main').count()===1);
   await context.close();
  }
  const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();await page.goto(base+'/receipts.html');
  check('No-script download and limits remain readable',await page.locator('noscript').isVisible());await context.close();
  check('No console/page errors',errors.length===0);
  check('No writes or third-party requests',network.every(r=>r.method==='GET'&&r.url.startsWith(base+'/')));
  console.log(JSON.stringify({passed:true,checks:checks.length,output}));
 }catch(e){errors.push(String(e));console.error(e);process.exitCode=1;}
 finally{await browser?.close();await new Promise(r=>server.close(r));await fs.writeFile(path.join(output,'browser.json'),JSON.stringify({checked_at:new Date().toISOString(),scope:'Local static UI and Web Crypto only; no native or hosted execution',passed:process.exitCode!==1,checks,errors,requests:network},null,2)+'\n');}
})();
