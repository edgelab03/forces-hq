/* Actual app journeys. Source-unavailable is expected until official docs can be indexed. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');
const url=process.env.APP_URL||'http://127.0.0.1:8502';
const {go,settled}=require('./browser_helpers.cjs');
async function choose(p,label,value){
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
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try{
 for(const width of [360,390]){
  const context=await b.newContext({viewport:{width,height:844},isMobile:true,hasTouch:true,acceptDownloads:true});
  const p=await context.newPage();await p.goto(url);await settled(p);
  assert.equal(await p.getByRole('combobox',{name:'Go to section',exact:true}).count(),0);
  const input=p.getByRole('textbox',{name:'Ask Forces HQ',exact:true});
  await input.fill('Can I claim my lunch back today?');await p.getByRole('textbox',{name:'Ask Forces HQ',exact:true}).press('Enter');await settled(p);
  await p.getByRole('heading',{name:'Meals and subsistence',exact:true}).waitFor();
  assert.equal(await p.getByText('Duty mileage and travel',{exact:true}).count(),0);
  await p.getByText('Unable to verify entitlement against current policy',{exact:true}).waitFor();
  await go(p,'Money');await go(p,'Policy');
  assert.equal(await p.getByRole('textbox',{name:'What do you need help with?',exact:true}).inputValue(),'Can I claim my lunch back today?');
  const question=p.getByRole('textbox',{name:'What do you need help with?',exact:true});
  await question.fill('What is the relevant JSP for claiming duty mileage?');await question.press('Tab');await settled(p);
  await p.getByRole('heading',{name:'Duty mileage and travel',exact:true}).waitFor();
  await p.getByText('Unable to verify entitlement against current policy',{exact:true}).waitFor();
  await go(p,'Profile');await choose(p,'Service','Royal Navy');
  const salary=p.getByRole('spinbutton',{name:'Verified annual pensionable earnings (£) — optional',exact:true});await salary.fill('47000');await salary.press('Tab');
  await p.getByText('I have checked this pensionable earnings amount against official documentation',{exact:true}).click();
  await p.getByRole('button',{name:'Update linked demo profile',exact:true}).click();await settled(p);
  await go(p,'Policy');await p.getByText('Royal Navy · Sergeant',{exact:false}).waitFor();
  await go(p,'Career');await p.getByRole('button',{name:'Add milestone',exact:true}).click();await p.getByText('Objectives agreed',{exact:false}).first().waitFor();await settled(p);
  await go(p,'Profile');
  await p.getByText('Save or restore an encrypted profile',{exact:true}).click();
  const password='fictional browser test passphrase';
  await p.getByRole('textbox',{name:'Backup passphrase (at least 12 characters)',exact:true}).fill(password);
  await p.getByRole('button',{name:'Prepare encrypted profile',exact:true}).click();await settled(p);
  const downloading=p.waitForEvent('download');await p.getByRole('button',{name:'Download encrypted profile',exact:true}).click();const download=await downloading;
  const data=fs.readFileSync(await download.path());assert.equal(data.includes(Buffer.from('Royal Navy')),false);
  // Restore in a separate browser context to verify persistence beyond session state.
  const other=await b.newContext({viewport:{width,height:844},isMobile:true,hasTouch:true});const restored=await other.newPage();await restored.goto(url);await settled(restored);await go(restored,'Profile');
  await restored.getByText('Save or restore an encrypted profile',{exact:true}).click();
  await restored.locator('input[type=file]').setInputFiles({name:'profile.fhq',mimeType:'application/octet-stream',buffer:data});
  await restored.getByRole('textbox',{name:'Restore passphrase',exact:true}).fill(password);
  await restored.getByText('Replace my current structured profile, career dates and benefit progress from this file',{exact:true}).click();
  await restored.getByRole('button',{name:'Restore encrypted profile',exact:true}).click();await settled(restored);
  try {
    await restored.waitForFunction(()=>document.querySelector('input[aria-label="Service"]')?.value==='Royal Navy',{},{timeout:10000});
  } catch (error) {
    await restored.screenshot({path:'/tmp/forces-restore-failure.png',fullPage:true});
    console.error(await restored.locator('[data-testid=stAlert]').allTextContents());
    throw error;
  }
  assert.equal(await restored.getByRole('combobox',{name:'Service',exact:true}).inputValue(),'Royal Navy');
  await go(restored,'Money');await restored.getByRole('button',{name:'Pay & pensions',exact:true}).click();await settled(restored);
  assert.equal(Number(await restored.getByRole('spinbutton',{name:'Current annual pensionable salary (£) — check payslip',exact:true}).inputValue()),47000);
  await go(restored,'Career');await restored.getByText('Objectives agreed',{exact:false}).first().waitFor();
  assert.equal(await restored.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await restored.screenshot({path:`/tmp/forces-connected-${width}.png`});
  await other.close();await context.close();console.log(`PASS ${width}px: meals/mileage separation, clarification retention, profile cross-links, encrypted file download and new-session restore, salary reuse and career persistence`);
 }
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
