const assert=require('node:assert/strict');
async function settled(p){await p.getByText('Forces HQ •',{exact:false}).last().waitFor();await p.waitForFunction(()=>document.querySelectorAll('[data-testid=stSkeleton]').length===0&&document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-script-state')==='notRunning'&&document.querySelectorAll('[data-stale="true"]').length===0);assert.equal(await p.locator('[data-testid=stException]').count(),0);}
async function go(p,name){
 const tab={Policy:'Ask',Claims:'Explore',Career:'Explore',Profile:'Me'}[name]||name;
 await p.locator('.st-key-app_navigation').getByRole('button',{name:tab,exact:true}).click();
 const headings={Money:'Your money, at a glance',Ask:'🔎 Ask Forces HQ',Me:'🎖️ My military profile',Explore:'🎯 Entitlements explorer'};
 await(tab==='Home'?p.locator('.st-key-welcome'):p.getByRole('heading',{name:headings[tab],exact:true})).waitFor();await settled(p);
 if(name==='Career'){await p.getByRole('button',{name:'Career',exact:true}).click();await p.getByRole('heading',{name:'📅 Career & reporting milestones',exact:true}).waitFor();await settled(p);}
}
module.exports={go,settled};
