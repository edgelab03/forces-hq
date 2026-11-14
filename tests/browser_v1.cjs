/* End-to-end real app. Production has no approved policy pack: assert abstention. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');
const url=process.env.APP_URL||'http://127.0.0.1:8511';
const {go,settled}=require('./browser_helpers.cjs');
async function select(p,label,value){
 let failure;
 for(let attempt=0;attempt<3;attempt++){
  await settled(p);const combo=p.getByRole('combobox',{name:label,exact:true}).last();
  try{
   await combo.click();await p.getByRole('listbox').waitFor({timeout:3000});
   if(await p.getByRole('option',{name:value,exact:true}).count()===0)await combo.press('End');
   await p.getByRole('option',{name:value,exact:true}).click();
   await p.waitForFunction(({label,value})=>Array.from(document.querySelectorAll('input')).some(e=>e.getAttribute('aria-label')===label&&e.value===value),{label,value});
   await settled(p);return;
  }catch(error){failure=error;await settled(p);if(await p.getByRole('listbox').isVisible())await combo.press('Escape');}
 }
 throw failure;
}
async function continueTo(p,step){await p.getByRole('button',{name:'Continue',exact:true}).click();await p.getByText(step,{exact:true}).waitFor();await settled(p);}
async function noOverflow(p){assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});try{
for(const width of [360,390]){
 const context=await browser.newContext({viewport:{width,height:844},isMobile:true,hasTouch:true,acceptDownloads:true});const p=await context.newPage();await p.goto(url);await settled(p);
 for(const [rank,years,query] of [['Private / equivalent',1,'Can I claim my lunch back yesterday?'],['Warrant Officer Class 1',20,'Can I claim an evening meal on detached duty while on exercise?']]){
  await go(p,'Profile');await select(p,'Rank',rank);await p.getByRole('spinbutton',{name:'Completed qualifying years (self-reported)',exact:true}).last().fill(String(years));await p.getByRole('spinbutton',{name:'Completed qualifying years (self-reported)',exact:true}).last().press('Tab');
  await p.getByRole('button',{name:'Update linked demo profile',exact:true}).click();await settled(p);assert.equal(Number(await p.getByRole('spinbutton',{name:'Completed qualifying years (self-reported)',exact:true}).last().inputValue()),years);
  await go(p,'Home');await p.getByRole('textbox',{name:'Ask Forces HQ',exact:true}).fill(query);await p.getByRole('textbox',{name:'Ask Forces HQ',exact:true}).press('Enter');
  await p.getByRole('heading',{name:'Meals and subsistence',exact:true}).waitFor();await p.getByText('Unable to verify entitlement against current policy',{exact:true}).waitFor();
  assert.equal(await p.getByRole('heading',{name:'Duty mileage and travel',exact:true}).count(),0);await noOverflow(p);
  await p.getByText('Evidence, exceptions and reasoning',{exact:true}).click();await p.getByText('Source unavailable for a verified decision:',{exact:false}).waitFor();
  assert.equal(await p.getByRole('link',{name:'Official publication — JSP 752',exact:true}).getAttribute('href'),'https://www.gov.uk/government/publications/jsp-752-tri-service-regulations-for-expenses-and-allowances');
  assert.equal(await p.getByRole('link',{name:'Open exact supporting provision',exact:true}).count(),0);
 }
 await p.getByRole('textbox',{name:'What do you need help with?',exact:true}).fill('Can I claim duty mileage for an authorised journey yesterday?');await p.getByRole('textbox',{name:'What do you need help with?',exact:true}).press('Tab');await p.getByRole('heading',{name:'Duty mileage and travel',exact:true}).waitFor();await p.getByText('Unable to verify entitlement against current policy',{exact:true}).waitFor();
 await go(p,'Home');await p.getByRole('button',{name:'Housing',exact:true}).click();await p.getByRole('heading',{name:'Your home-buying plan',exact:true}).waitFor();await settled(p);
 await continueTo(p,'2 of 5 · Assess');await p.getByText('Unable to verify entitlement against current policy',{exact:true}).waitFor();
 await p.getByRole('button',{name:'Ask a related housing question',exact:true}).click();await p.getByRole('heading',{name:'Forces Help to Buy',exact:true}).waitFor();await p.getByRole('button',{name:'Continue your home-buying guide',exact:true}).click();await p.getByText('2 of 5 · Assess',{exact:true}).waitFor();
 await continueTo(p,'3 of 5 · Budget');await p.getByRole('button',{name:'Edit purchase figures',exact:true}).click();
 for(const [name,value] of [['Property price (£)','200000'],['Your cash deposit (£)','20000'],['Proposed advance — assumption (£)','10000'],['Proposed mortgage (£)','170000']])await p.getByRole('spinbutton',{name,exact:true}).fill(value);
 await p.getByText('Tax, legal and other costs',{exact:true}).click();await p.getByRole('spinbutton',{name:'Solicitor / conveyancing quote (£)',exact:true}).fill('1500');await p.getByRole('button',{name:'Save purchase figures',exact:true}).click();await p.getByText('£1,500',{exact:true}).waitFor();
 await p.getByText('Wales',{exact:true}).click();await settled(p);assert.equal(await p.getByRole('link',{name:'Welsh Government LTT',exact:true}).getAttribute('href'),'https://www.gov.wales/land-transaction-tax-rates-and-bands');await noOverflow(p);
 await continueTo(p,'4 of 5 · Prepare');await p.getByText('The exact JPA process, current forms, deadlines and approval/legal sequence are not verified.',{exact:false}).waitFor();
 await p.getByText('Refund of Legal Expenses — separate assessment',{exact:true}).click();await p.getByRole('button',{name:'Check legal-expense circumstances separately',exact:true}).click();await p.getByRole('heading',{name:'Refund of Legal Expenses — separate check',exact:true}).waitFor();await p.getByRole('button',{name:'Continue your home-buying guide',exact:true}).click();await p.getByText('4 of 5 · Prepare',{exact:true}).waitFor();
 await continueTo(p,'5 of 5 · Progress');await p.getByText('Ask the lender or broker whether the proposed funding is acceptable',{exact:true}).click();await settled(p);await p.getByRole('button',{name:'Open profile saving',exact:true}).click();await p.getByRole('heading',{name:'🎖️ My military profile',exact:true}).waitFor();
 await p.getByText('Save or restore an encrypted profile',{exact:true}).click();const password='fictional V1 browser passphrase';await p.getByRole('textbox',{name:'Backup passphrase (at least 12 characters)',exact:true}).fill(password);await p.getByRole('button',{name:'Prepare encrypted profile',exact:true}).click();await settled(p);
 const downloading=p.waitForEvent('download');await p.getByRole('button',{name:'Download encrypted profile',exact:true}).click();const file=await downloading;const bytes=fs.readFileSync(await file.path());
 const next=await browser.newContext({viewport:{width,height:844},isMobile:true,hasTouch:true});const restored=await next.newPage();await restored.goto(url);await settled(restored);await go(restored,'Profile');await restored.getByText('Save or restore an encrypted profile',{exact:true}).click();await restored.locator('input[type=file]').setInputFiles({name:'plan.fhq',mimeType:'application/octet-stream',buffer:bytes});await restored.getByRole('textbox',{name:'Restore passphrase',exact:true}).fill(password);await restored.getByText('Replace my current structured profile, career dates and benefit progress from this file',{exact:true}).click();await restored.getByRole('button',{name:'Restore encrypted profile',exact:true}).click();await restored.getByText('Linked profile updated for this session.',{exact:false}).waitFor();
 await go(restored,'Home');await restored.getByRole('button',{name:'Housing',exact:true}).click();await restored.getByText('5 of 5 · Progress',{exact:true}).waitFor();assert.equal(await restored.getByRole('checkbox',{name:'Ask the lender or broker whether the proposed funding is acceptable',exact:true}).isChecked(),true);
 await restored.getByText('I have already claimed or completed this journey',{exact:true}).click();await settled(restored);await go(restored,'Home');assert.equal(await restored.getByRole('button',{name:'Plan a home purchase',exact:true}).count(),0);await noOverflow(restored);await restored.screenshot({path:`/tmp/forces-v1-completed-${width}.png`});
 console.log(`PASS ${width}px: Private/WO1 meals, mileage abstention, housing handoff, complete FHTB planning flow, purchase arithmetic, tax routing, separate RLE, encrypted cross-session checklist and completed suppression`);
 await next.close();await context.close();
}
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
