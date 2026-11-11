// Static presentation checks only. Never starts IRIS or evaluates an agent.
const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require(path.resolve(__dirname,'../web/node_modules/playwright'));
const output=path.resolve(process.argv[3]||'.local/agent-value-browser');
(async()=>{
 await fs.mkdir(output,{recursive:true});let server,base=process.argv[2],browser;
 if(!base){const root=path.resolve(__dirname,'../docs/site');server=http.createServer(async(req,res)=>{
  try{const p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));if(p!==root&&!p.startsWith(root+path.sep))throw Error('outside root');const stat=await fs.stat(p),file=stat.isDirectory()?path.join(p,'index.html'):p;res.writeHead(200,{'Content-Type':{'.html':'text/html','.css':'text/css','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.woff2':'font/woff2','.png':'image/png','.webp':'image/webp','.jpg':'image/jpeg'}[path.extname(file)]||'application/octet-stream'});res.end(await fs.readFile(file));}catch{res.writeHead(404);res.end('Not found');}
 });await new Promise(r=>server.listen(0,'127.0.0.1',r));base='http://127.0.0.1:'+server.address().port+'/';}
 const checks=[],errors=[],requests=[];const check=(name,ok)=>{assert.ok(ok,name);checks.push(name);};
 try{
  browser=await chromium.launch({channel:process.env.SILENTSHIFT_CHROME_CHANNEL||'chrome'});
  for(const width of [1440,375]){
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
   const response=await page.goto(base+'agent-value.html');check(width+': page returns 200',response.status()===200);
   check(width+': intended page title',await page.title()==='What the agent saw — SilentShift');
   check(width+': all three source cases rendered',await page.locator('article.value-case').count()===3);
   check(width+': no horizontal page overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const headline=await page.locator('.heldout-summary').innerText();check(width+': headline retains review cost and worse third trial',headline.includes('21.5%')&&headline.includes('12.5%')&&headline.includes('30/48')&&headline.includes('counterfactual'));
   await page.screenshot({path:path.join(output,'intro-'+width+'.png')});
   await page.getByRole('navigation',{name:'Recorded examples'}).getByRole('link',{name:'HO-045 · The quantity changed in prose',exact:true}).click();
   check(width+': example links preserve direct URL',page.url().endsWith('#HO-045'));
   const card=page.locator('#HO-045');check(width+': actual amendment and finding are readable',(await card.innerText()).includes('reduced to 80 EA')&&(await card.innerText()).includes('Approved contract reduces quantity to 80 EA; 100 EA violates current authority.'));
   check(width+': policy hold is not relabelled as correct',(await card.innerText()).includes('still scored incorrect'));
   check(width+': pending task is not a claimed human resolution',(await card.innerText()).includes('no reviewer decision or eventual delivery is recorded'));
   await card.locator('details').first().getByText('Inspect all three recorded trials and the frozen label',{exact:true}).click();
   check(width+': source disclosure expands',await card.locator('table').isVisible());
   check(width+': all trials, not a selected best run',await card.locator('tbody tr').count()===3);
   await page.screenshot({path:path.join(output,'case-'+width+'.png')});
   const data=await context.request.get(base+'assets/agent-value.json');check(width+': static source extract resolves',data.status()===200);check(width+': extract has the selected actual IDs',JSON.stringify((await data.json()).cases.map(c=>c.id))===JSON.stringify(['HO-045','HO-030','HO-017']));
   await page.goto(base);await page.getByRole('link',{name:'What the agent saw ↗',exact:true}).click();check(width+': landing reaches first prose example',page.url().includes('agent-value.html#HO-045'));
   await page.goto(base+'evidence-tour.html');await page.getByRole('link',{name:'What the agent saw that the rules missed ↗',exact:true}).click();check(width+': recorded tour reaches prose example',page.url().includes('agent-value.html#HO-045'));
   await page.goto(base+'agent-value.html');await page.keyboard.press('Tab');check(width+': keyboard starts with skip link',await page.locator('.skip-link').evaluate(e=>e===document.activeElement));await page.keyboard.press('Enter');check(width+': skip link reaches main',page.url().endsWith('#main')&&await page.locator('#main').evaluate(e=>e===document.activeElement));
   await context.close();
  }
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}}),page=await context.newPage();await page.goto(base+'agent-value.html');check('No-JS cases and metrics remain readable',await page.locator('article.value-case').count()===3&&(await page.locator('.heldout-summary').innerText()).includes('6/23'));
  await page.locator('#HO-030 > details > summary').click();check('No-JS original trial disclosure works',await page.locator('#HO-030 table').isVisible());await context.close();
  check('No console or page errors',errors.length===0);check('Only static local GET requests',requests.every(r=>r.method==='GET'&&r.url.startsWith(base)));
  console.log(JSON.stringify({passed:true,checks:checks.length,scope:'Static browser presentation, no evaluation or native execution'}));
 }catch(e){errors.push(String(e));process.exitCode=1;console.error(e);}
 finally{await browser?.close();if(server)await new Promise(r=>server.close(r));await fs.writeFile(path.join(output,'browser.json'),JSON.stringify({checked_at:new Date().toISOString(),base,passed:process.exitCode!==1,checks,errors,requests,scope:'Static historical-record presentation only'},null,2)+'\n');}
})();
