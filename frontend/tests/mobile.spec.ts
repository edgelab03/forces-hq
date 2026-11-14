import { test, expect, type Page } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';

const screenshots = path.join(process.cwd(), 'docs/screenshots');
async function ready(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  await expect(page.getByRole('navigation', { name: 'Main navigation' })).toBeVisible();
}
async function screenshot(page: Page, name: string) {
  fs.mkdirSync(screenshots, { recursive: true });
  await page.screenshot({ path: path.join(screenshots, `${name}-${page.viewportSize()!.width}.png`), animations: 'disabled' });
}
async function noOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  const nav = await page.locator('.bottom-nav').boundingBox();
  const main = await page.locator('main').boundingBox();
  expect(main!.y + main!.height).toBeLessThanOrEqual(nav!.y + 1);
}

test('Home renders the design, useful cards and five native navigation links', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('/'); await ready(page);
  await expect(page.getByRole('heading', { name: 'Hello, Alex.' })).toBeVisible();
  await expect(page.locator('body')).toHaveCSS('background-color', 'rgb(247, 247, 242)');
  await expect(page.locator('.ask-card')).toHaveCSS('background-color', 'rgb(37, 72, 62)');
  await expect(page.locator('body')).toHaveCSS('color', 'rgb(38, 61, 54)');
  await expect(page.locator('.quick-card').first()).toHaveCSS('background-color', 'rgb(255, 255, 255)');
  const cards = await page.locator('.quick-card').all();
  expect(cards).toHaveLength(4);
  const boxes = await Promise.all(cards.map(card => card.boundingBox()));
  expect(boxes[0]!.y).toBe(boxes[1]!.y);
  expect(boxes[2]!.y).toBe(boxes[3]!.y);
  expect(boxes[1]!.x).toBeGreaterThan(boxes[0]!.x);
  const bottom = await page.locator('.bottom-nav').boundingBox();
  expect(boxes[3]!.y + boxes[3]!.height).toBeLessThanOrEqual(bottom!.y);
  const links = page.getByRole('navigation').getByRole('link');
  await expect(links).toHaveCount(5);
  for (const link of await links.all()) {
    const box = await link.boundingBox();
    expect(box!.width).toBeGreaterThanOrEqual(44);
    expect(box!.height).toBeGreaterThanOrEqual(44);
  }
  await noOverflow(page); await screenshot(page, 'home');
  const scroll = page.locator('.home-content');
  const sizes = await scroll.evaluate(e => ({ height: e.clientHeight, total: e.scrollHeight }));
  expect(sizes.total / sizes.height).toBeLessThan(1.9);
  await scroll.evaluate(e => e.scrollTop = e.scrollHeight);
  await expect(page.getByText('DEMO OPPORTUNITY', { exact: true })).toBeVisible();
  await screenshot(page, 'home-overview');
  expect(errors).toEqual([]);
});

test('Lunch conversation continues, keeps answers through history/reload and resets', async ({ page }) => {
  await page.goto('/'); await ready(page);
  await page.getByRole('textbox', { name: 'Your question' }).fill('Can I claim my lunch from yesterday?');
  await page.getByRole('button', { name: 'Send question to Ask' }).click();
  await expect(page).toHaveURL(/\/ask$/);
  await expect(page.getByRole('button', { name: 'Yes, I was away', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Yes, I was away', exact: true }).click();
  await expect(page.getByText('Thanks, that helps.', { exact: false })).toBeVisible();
  await expect(page.getByRole('log')).toContainText('Can I claim my lunch from yesterday?');
  await screenshot(page, 'ask');
  await page.getByRole('link', { name: 'Home', exact: true }).click();
  await page.goBack();
  await expect(page.getByRole('log')).toContainText('Yes, I was away');
  await page.reload(); await ready(page);
  await expect(page.getByRole('button', { name: 'Yes, it was authorised', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Yes, it was authorised', exact: true }).click();
  await page.getByRole('textbox', { name: 'Your message' }).fill('I paid for it myself; no meal was provided.');
  await page.getByRole('textbox', { name: 'Your message' }).press('Enter');
  await expect(page.getByRole('region', { name: 'Your demo context' })).toBeVisible();
  await expect(page.getByRole('log')).toContainText('I haven’t assessed your eligibility or verified any policy.');
  await expect(page.getByRole('log')).not.toContainText(/you are eligible|appears eligible|JSP\s*\d/i);
  await noOverflow(page); await screenshot(page, 'ask-complete');
  await page.getByRole('button', { name: 'Start a new demo conversation' }).click();
  await expect(page.getByRole('log')).not.toContainText('I paid for it myself');
  await expect(page.getByRole('log')).toContainText('Hi Alex.');
});

test('Chat composer stays clear of navigation in a reduced keyboard viewport', async ({ page }) => {
  await page.goto('/ask'); await ready(page);
  const width = page.viewportSize()!.width;
  const entry = page.getByRole('textbox', { name: 'Your message' });
  await entry.focus();
  await page.setViewportSize({ width, height: 440 });
  await entry.fill('Can I claim my lunch from yesterday?');
  await expect(page.getByRole('navigation')).toBeHidden();
  const input = await entry.boundingBox();
  expect(input!.y).toBeGreaterThan(0);
  expect(input!.y + input!.height).toBeLessThan(440);
  await page.getByRole('button', { name: 'Send message' }).click();
  await expect(page.getByRole('button', { name: 'Yes, I was away', exact: true })).toBeVisible();
  await expect(entry).toBeFocused();
  await expect(page.getByRole('navigation')).toBeHidden();
  await screenshot(page, 'ask-keyboard-height');
  // Exercise the VisualViewport branch independently of physical keyboard support.
  await page.evaluate(() => {
    Object.defineProperty(window.visualViewport, 'height', { configurable: true, value: 260 });
    document.querySelector<HTMLTextAreaElement>('textarea')!.focus();
    window.visualViewport!.dispatchEvent(new Event('resize'));
  });
  await expect(page.locator('html')).toHaveAttribute('data-keyboard', 'true');
  await expect(page.getByRole('navigation')).toBeHidden();
  const composer = await page.locator('.composer').boundingBox();
  expect(composer!.y + composer!.height).toBeLessThanOrEqual(260);
});

test('All out-of-scope cards and navigation open honest, keyboard-accessible preview sheets', async ({ page }) => {
  await page.goto('/'); await ready(page);
  for (const name of ['Pay', 'Pension', 'Learning']) {
    await page.getByRole('link', { name, exact: false }).filter({ has: page.locator('strong') }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByRole('dialog')).toContainText('Preview only');
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  }
  for (const name of ['Money', 'Explore', 'Me']) {
    await page.getByRole('navigation').getByRole('link', { name, exact: true }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.getByRole('button', { name: 'Close preview' }).click();
    await expect(page.getByRole('dialog')).toBeHidden();
  }
  await page.getByRole('button', { name: /Housing/ }).click();
  await expect(page).toHaveURL(/\/ask$/);
  await expect(page.getByRole('button', { name: 'Just exploring', exact: true })).toBeVisible();
});

test('Direct Ask entry, unknown text and malformed local demo state remain usable', async ({ page }) => {
  await page.goto('/ask'); await ready(page);
  await page.evaluate(() => sessionStorage.setItem('forces-hq-design-demo-v1', '{broken'));
  await page.reload(); await ready(page);
  await page.getByRole('textbox', { name: 'Your message' }).fill('Tell me about something outside this demo');
  await page.getByRole('button', { name: 'Send message' }).click();
  await expect(page.getByRole('log')).toContainText('This demo can walk through');
  await expect(page.getByRole('button', { name: 'Can I claim my lunch from yesterday?', exact: true })).toBeVisible();
});
