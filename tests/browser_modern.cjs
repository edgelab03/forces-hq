const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('playwright');
const {go,settled}=require('./browser_helpers.cjs');
const url=process.env.APP_URL||'http://127.0.0.1:8531';
async function noOverflow(p){assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});try{
fs.mkdirSync('/tmp/modern-forces',{recursive:true});
for(const width of [360,390,412,768,1280]){
 const context=await browser.newContext({viewport:{width,height:900},isMobile:width<600,hasTouch:width<600});const p=await context.newPage();await p.goto(url);await settled(p);
 assert.equal(await p.locator('[data-testid=stApp]').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(247, 247, 242)');
 assert.equal(await p.locator('.st-key-ask_panel').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(220, 239, 227)');
 assert.equal(await p.locator('.st-key-home_ask button').evaluate(e=>getComputedStyle(e).color),'rgb(255, 255, 255)');
 assert.equal(await p.getByRole('radiogroup',{name:'Primary navigation'}).count(),0);
 await noOverflow(p);
 const controls=p.locator('.st-key-app_navigation').getByRole('button');assert.equal(await controls.count(),5);
 for(const button of await controls.all()){
  const box=await button.boundingBox();assert.ok(box.width>=44&&box.height>=44);
  const text=button.locator('[data-testid=stMarkdownContainer]');assert.equal(await text.evaluate(e=>e.scrollWidth>e.clientWidth),false,'Nav label is truncated');
 }
 const cards=[];for(const label of ['Your pay','Housing','Pension','Learning'])cards.push(await p.getByRole('button',{name:label,exact:true}).boundingBox());
 assert.ok(Math.abs(cards[0].y-cards[1].y)<2&&cards[1].x>cards[0].x);assert.ok(Math.abs(cards[2].y-cards[3].y)<2&&cards[2].y>cards[0].y);
 assert.equal(await p.getByRole('button',{name:'Voice input unavailable',exact:true}).isDisabled(),true);
 assert.equal(await p.getByRole('button',{name:'Continue your plan',exact:true}).count(),0);
 await p.screenshot({path:`/tmp/modern-forces/home-${width}.png`});
 await p.getByRole('button',{name:'Your pay',exact:true}).click();await p.getByRole('heading',{name:'Your money, at a glance',exact:true}).waitFor();await settled(p);
 await p.getByRole('button',{name:'Back',exact:true}).click();await p.locator('.st-key-welcome').waitFor();await settled(p);
 await p.getByRole('button',{name:'Housing',exact:true}).click();await p.getByRole('heading',{name:'Your home-buying plan',exact:true}).waitFor();await settled(p);
 await p.getByRole('button',{name:'Continue',exact:true}).click();await p.getByText('2 of 5 · Assess',{exact:true}).waitFor();
 await go(p,'Home');await p.getByRole('button',{name:'Continue your plan',exact:true}).click();await p.getByText('2 of 5 · Assess',{exact:true}).waitFor();
 await go(p,'Home');await p.getByRole('button',{name:'Pension',exact:true}).click();await p.getByRole('heading',{name:'🏦 Armed Forces pension planning',exact:true}).waitFor();await settled(p);
 await go(p,'Home');await p.getByRole('button',{name:'Learning',exact:true}).click();await p.getByRole('heading',{name:'Learning & development',exact:true}).waitFor();await settled(p);
 assert.equal(await p.getByRole('combobox',{name:'Milestone',exact:true}).count(),1);
 await p.getByRole('button',{name:'Open profile',exact:true}).click();await p.getByRole('heading',{name:'🎖️ My military profile',exact:true}).waitFor();await settled(p);
 await p.getByRole('button',{name:'Back',exact:true}).click();await p.getByRole('heading',{name:'Learning & development',exact:true}).waitFor();await settled(p);
 await go(p,'Home');const question='Can I claim my lunch back yesterday?';
 await p.getByRole('textbox',{name:'Ask Forces HQ',exact:true}).fill(question);await p.getByRole('textbox',{name:'Ask Forces HQ',exact:true}).press('Enter');
 await p.getByRole('heading',{name:'Meals and subsistence',exact:true}).waitFor();await settled(p);
 assert.equal(await p.getByRole('textbox',{name:'What do you need help with?',exact:true}).inputValue(),question);
 for(const name of ['Money','Explore','Me','Ask']){await go(p,name);await noOverflow(p);assert.equal(await p.locator('.st-key-app_navigation button[kind=primary]:visible').count(),1);}
 assert.equal(await p.getByRole('textbox',{name:'What do you need help with?',exact:true}).inputValue(),question);
 // A resized viewport approximates space lost to a keyboard; actual Android remains manual.
 await p.setViewportSize({width,height:500});const entry=p.getByRole('textbox',{name:'What do you need help with?',exact:true});await entry.focus();await entry.scrollIntoViewIfNeeded();
 const inputBox=await entry.boundingBox();const nav=await p.locator('.st-key-app_navigation').boundingBox();assert.ok(inputBox.y>=0&&inputBox.y+inputBox.height<=nav.y,'Question input overlaps bottom controls in a reduced viewport');
 await p.setViewportSize({width,height:900});await settled(p);
 await p.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop=e.scrollHeight);const footer=await p.getByText('Forces HQ •',{exact:false}).boundingBox();const bottom=await p.locator('.st-key-app_navigation').boundingBox();assert.ok(footer.y+footer.height<=bottom.y,'Bottom nav obscures page content');
 await noOverflow(p);console.log(`PASS ${width}px: light tokens, 2×2 cards, five icon tabs, no label clipping/overflow, all destinations, back/history, question and journey retention, reduced-viewport input clearance`);
 await context.close();
}
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
