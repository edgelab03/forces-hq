/* Run against a local server with Playwright and Chromium installed. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const url = process.env.APP_URL || 'http://127.0.0.1:8502';
const artifacts = process.env.ARTIFACT_DIR || '/tmp/forces-hq-phase1';
const sections = ['🏠 Dashboard', '🎖️ My profile', '💷 My money', '🎯 Entitlements',
  '📚 JSP finder', '📅 My career', '✍️ Achievement assistant', '🏡 Life & future', '🏦 Pension planner'];
const headings = ['Welcome back', '🎖️ My military profile', '💷 My money',
  '🎯 Entitlements explorer', '🔎 Ask Forces HQ', '📅 Career & reporting milestones',
  '✍️ Achievement & appraisal preparation', '🏡 Military life & future', '🏦 Armed Forces pension planning'];

async function settled(page) {
  await page.getByText('Forces HQ V0.9.1 •', { exact: false }).waitFor();
  await page.waitForFunction(() => document.querySelectorAll('[data-testid="stSkeleton"]').length === 0);
  assert.equal(await page.locator('[data-testid="stException"]').count(), 0);
}
async function section(page, index) {
  const destination = index === 0 ? 'Home' : index === 1 ? 'Profile' : [2,8].includes(index) ? 'Money' : 'Explore';
  await page.getByRole('radiogroup', {name:'Primary navigation'}).getByText(destination,{exact:true}).click();
  await settled(page);
  if (destination === 'Explore' || destination === 'Money') {
    const tools = page.locator('details').filter({hasText:destination+' tools'}).first();
    await tools.waitFor();
    if (!(await tools.evaluate(el => el.open))) await page.getByText(destination+' tools',{exact:true}).click();
    await page.getByRole('button',{name:sections[index],exact:true}).click();
  }
  await (index === 0 ? page.getByText('Welcome back',{exact:true}) : page.getByRole('heading',{name:headings[index],exact:true})).waitFor();
  await settled(page);
}
async function main() {
  fs.mkdirSync(artifacts, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',
    headless: true, args: ['--no-sandbox'],
  });
  try {
    for (const width of [360, 390, 1280]) {
      const context = await browser.newContext({
        viewport: { width, height: 844 }, isMobile: width < 640, hasTouch: width < 640,
        ...(width < 640 ? { userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36' } : {}),
      });
      const page = await context.newPage();
      if (process.env.BROWSER_CPU_RATE) {
        const session = await context.newCDPSession(page);
        await session.send('Emulation.setCPUThrottlingRate', { rate: Number(process.env.BROWSER_CPU_RATE) });
      }
      await page.goto(url);
      await settled(page);
      await page.screenshot({ path: path.join(artifacts, `home-${width}.png`) });
      const header = await page.getByRole('heading', {name:'🛡️ Forces HQ',exact:true}).boundingBox();
      assert.ok(header && header.y >= 48, 'Branding is covered by Streamlit header');
      const policy = await page.getByRole('button', {name:'Policy Find JSP answers',exact:true}).boundingBox();
      const claims = await page.getByRole('button', {name:'Claims JPA guidance',exact:true}).boundingBox();
      assert.ok(policy && claims && Math.abs(policy.y-claims.y)<2 && claims.x>policy.x, 'Home cards must stay in two columns');
      const nav = await page.locator('.st-key-app_navigation').boundingBox();
      assert.ok(policy.y+policy.height<nav.y, 'Bottom navigation covers dashboard cards');
      for (const [label,index] of [['Policy Find JSP answers',4],['Claims JPA guidance',3],['Money Pay and pensions',8],['Career Personal development',5]]) {
        await page.getByRole('button',{name:label,exact:true}).click();
        await page.getByRole('heading',{name:headings[index],exact:true}).waitFor();
        await settled(page);
        await page.getByRole('radiogroup',{name:'Primary navigation'}).getByText('Home',{exact:true}).click();
        await page.getByText('Welcome back',{exact:true}).waitFor();
        await settled(page);
      }
      const primary = page.getByRole('radiogroup', { name: 'Primary navigation' });
      for (const [name, index] of [['Explore',3], ['Money',2], ['Profile',1], ['Home',0]]) {
        await primary.getByText(name, { exact: true }).click();
        await (index === 0 ? page.getByText('Welcome back', {exact:true}) : page.getByRole('heading', { name: headings[index], exact: true })).waitFor();
        await settled(page);
        for (const label of await primary.locator('label').all()) {
          const target = await label.boundingBox();
          assert.ok(target && target.height >= 44 && target.width >= 44, 'Primary touch target too small');
        }
      }
      await page.getByRole('button', { name: '⌕  Ask a military question', exact: true }).click();
      await page.getByRole('heading', { name: headings[4], exact: true }).waitFor();
      await settled(page);
      for (let index = 0; index < sections.length; index++) {
        await section(page, index);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false,
          `Horizontal document overflow at ${width}px: ${sections[index]}`);
        console.log(`PASS ${width}px section: ${sections[index]}`);
        // Streamlit scrolls inside its main panel rather than the document.
        await page.locator('[data-testid="stMain"]').evaluate(el => { el.scrollTop = el.scrollHeight; });
        const box = await page.locator('.st-key-app_navigation').boundingBox();
        assert.ok(box && box.y >= 0 && box.y + box.height <= 844 && box.height <= 80,
          `Navigation left the screen at ${width}px: ${sections[index]} (${JSON.stringify(box)})`);
        const footer = await page.getByText('Forces HQ V0.9.1 •', {exact:false}).boundingBox();
        assert.ok(footer && footer.y+footer.height <= box.y, 'Bottom navigation obscures scrollable content');
      }
      await section(page, 2);
      const income = page.getByRole('spinbutton', { name: 'Monthly take-home income (£)', exact: true });
      await income.fill('3500');
      await income.press('Tab');
      await page.getByText('£1,250', { exact: true }).waitFor();
      await section(page, 0);
      await section(page, 2);
      assert.equal(await income.inputValue(), '3500');
      await section(page, 1);
      const join = page.getByLabel('Date joined', { exact: true });
      assert.equal(await join.isDisabled(), true);
      const joinId = await join.getAttribute('id');
      await page.getByText('Record enlistment date', { exact: true }).click();
      await page.waitForFunction(id => {
        const input = document.getElementById(id);
        return input && !input.disabled;
      }, joinId);
      await settled(page);
      await section(page, 6);
      await page.getByRole('textbox', { name: 'What did you do?', exact: true }).fill('Led a fictional exercise');
      await page.getByRole('textbox', { name: 'What did you do?', exact: true }).press('Tab');
      await page.getByRole('textbox', { name: 'What changed? Include evidence you could verify.', exact: true }).fill('Trained 12 fictional people');
      await page.getByRole('textbox', { name: 'What changed? Include evidence you could verify.', exact: true }).press('Tab');
      await page.getByRole('button', { name: 'Add practice achievement', exact: true }).click();
      const draft = page.getByRole('textbox', { name: 'Editable draft — review all claims before use', exact: true });
      await draft.waitFor();
      // Deliberately do not wait between blur-triggered reruns. Active fields
      // must retain new typing while an earlier field's response is in flight.
      for (let attempt = 0; attempt < 3; attempt++) {
        const action = page.getByRole('textbox', { name: 'What did you do?', exact: true });
        const result = page.getByRole('textbox', { name: 'What changed? Include evidence you could verify.', exact: true });
        const expected = `Rapid fictional achievement ${attempt}`;
        await action.fill(expected);
        await action.press('Tab');
        await result.fill(`Verified fictional result ${attempt}`);
        await result.press('Tab');
        await page.getByRole('button', { name: 'Add practice achievement', exact: true }).click();
        await page.waitForFunction(text => {
          const input = document.querySelector('textarea[aria-label="Editable draft — review all claims before use"]');
          return input && input.value.includes(text);
        }, expected);
      }
      await draft.fill('Reviewed fictional draft for download');
      await draft.press('Tab');
      await settled(page);
      await section(page, 0);
      await section(page, 6);
      assert.equal(await draft.inputValue(), 'Reviewed fictional draft for download');
      const downloadEvent = page.waitForEvent('download');
      await page.getByRole('button', { name: 'Download practice draft', exact: true }).click();
      const download = await downloadEvent;
      assert.equal(fs.readFileSync(await download.path(), 'utf8'), 'Reviewed fictional draft for download');
      await page.screenshot({ path: path.join(artifacts, `achievement-${width}.png`) });
      await section(page, 0);
      await page.locator('[data-testid="stMain"]').evaluate(el => { el.scrollTop = 0; });
      await page.screenshot({ path: path.join(artifacts, `dashboard-${width}.png`) });
      console.log(`PASS ${width}px: all nine pages, bottom navigation, retained income and draft, reactive date control, rapid achievement entry, exact edited download`);
      await context.close();
    }
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
