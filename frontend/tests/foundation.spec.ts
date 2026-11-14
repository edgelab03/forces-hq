import { test, expect, type Page } from '@playwright/test';
import fs from 'node:fs';

async function saveEdits(page: Page) {
  const response = page.waitForResponse(r => r.url().endsWith('/api/backend/profile') && r.request().method() === 'PUT');
  await page.getByRole('button', { name: 'Confirm profile', exact: true }).click();
  expect((await response).status()).toBe(200);
  await expect(page.getByRole('status')).toContainText('Profile confirmed');
}

async function confirmProfile(page: Page) {
  await page.goto('/me');
  await expect(page.getByLabel('Service', { exact: true })).toBeEnabled();
  await page.getByLabel('Service', { exact: true }).selectOption('Royal Navy');
  await page.getByLabel('Rank', { exact: true }).selectOption('Warrant Officer Class 1');
  await page.getByLabel('Service type', { exact: true }).selectOption('Regular');
  await page.getByLabel('Date joined (optional)', { exact: true }).fill('2005-01-01');
  await page.getByLabel('Date of birth (optional)', { exact: true }).fill('1985-01-01');
  const response = page.waitForResponse(r => r.url().endsWith('/api/backend/profile') && r.request().method() === 'PUT');
  await page.getByRole('button', { name: 'Confirm profile', exact: true }).click();
  const received = await response;
  expect(received.status()).toBe(200);
  const body = await received.json();
  expect(body.provenance.profile).toBe('user_confirmed');
  await expect(page.getByRole('status')).toContainText('Profile confirmed');
}

test('Real API profile, salary attestation, promotions and Home remain connected without plaintext storage', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await confirmProfile(page);
  await page.getByRole('link', { name: 'Circumstances', exact: true }).click();
  await page.getByLabel('Number of dependants', { exact: true }).fill('2');
  await page.getByLabel('AFPS 05', { exact: true }).check();
  await page.getByLabel('AFPS 15', { exact: true }).check();
  await page.getByLabel('Annual pensionable earnings (£, optional)', { exact: true }).fill('47000');
  await page.getByRole('checkbox', { name: /I checked this pensionable earnings/ }).check();
  await saveEdits(page);
  await page.getByRole('link', { name: 'History', exact: true }).click();
  await page.getByLabel('Rank attained', { exact: true }).selectOption('Sergeant');
  await page.getByLabel('Effective date', { exact: true }).fill('2015-01-01');
  await page.getByRole('button', { name: 'Add promotion', exact: true }).click();
  await saveEdits(page);
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'Home', exact: true }).click();
  await expect(page.getByText('Warrant Officer Class 1 · Royal Navy', { exact: true })).toBeVisible();
  await expect(page.getByText('£47,000.00', { exact: true })).toBeVisible();
  await expect(page.locator('main')).toContainText('Not a pay calculation');
  const stores = await page.evaluate(() => JSON.stringify({ local: { ...localStorage }, session: { ...sessionStorage } }));
  expect(stores).not.toMatch(/Royal Navy|Warrant Officer|47000|1985|2005/);
  expect(errors).toEqual([]);
  fs.mkdirSync('docs/screenshots/connected', { recursive: true });
  await page.screenshot({ path: `docs/screenshots/connected/home-${page.viewportSize()!.width}.png` });
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'Me', exact: true }).click();
  await expect(page.getByLabel('Service', { exact: true })).toHaveValue('Royal Navy');
  await page.screenshot({ path: `docs/screenshots/connected/profile-${page.viewportSize()!.width}.png` });
  await page.reload();
  await expect(page.getByLabel('Service', { exact: true })).toHaveValue('');
});

test('Encrypted export restores through the actual Python service in a separate browser context', async ({ page, browser, baseURL }) => {
  await confirmProfile(page);
  await page.getByRole('link', { name: 'Backup', exact: true }).click();
  const passphrase = 'test-only-encrypted-export-password';
  await page.getByLabel('Backup passphrase', { exact: true }).fill(passphrase);
  const downloaded = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download encrypted profile', exact: true }).click();
  const download = await downloaded;
  const bytes = fs.readFileSync((await download.path())!);
  expect(bytes.subarray(0, 5).toString()).toBe('FHQ1\n');
  expect(bytes.includes(Buffer.from('Royal Navy'))).toBe(false);
  await expect(page.getByLabel('Backup passphrase', { exact: true })).toHaveValue('');
  const other = await browser.newContext({ baseURL, viewport: page.viewportSize()!, httpCredentials: { username: process.env.FHQ_TEST_USERNAME || 'foundation-test', password: process.env.FHQ_TEST_PASSWORD || 'test-only-preview-password-not-for-production' } });
  try {
    const restored = await other.newPage(); await restored.goto('/me?section=backup');
    await restored.getByLabel('Encrypted profile file', { exact: true }).setInputFiles({ name: 'profile.fhq', mimeType: 'application/octet-stream', buffer: bytes });
    await restored.getByLabel('Restore passphrase', { exact: true }).fill('wrong test password');
    await restored.getByRole('checkbox', { name: 'Replace my current profile with the validated backup.' }).check();
    await restored.getByRole('button', { name: 'Restore encrypted profile', exact: true }).click();
    await expect(restored.getByRole('main').getByRole('alert')).toContainText('Check your profile');
    await restored.getByLabel('Restore passphrase', { exact: true }).fill(passphrase);
    await restored.getByRole('button', { name: 'Restore encrypted profile', exact: true }).click();
    await expect(restored.getByRole('status')).toContainText('Encrypted profile restored');
    await expect(restored.getByLabel('Restore passphrase', { exact: true })).toHaveValue('');
    await restored.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'Home', exact: true }).click();
    await expect(restored.getByText('Warrant Officer Class 1 · Royal Navy', { exact: true })).toBeVisible();
  } finally { await other.close(); }
});

test('Failed API update retains confirmed profile and exposes no backend credential', async ({ page }) => {
  await confirmProfile(page);
  await page.getByLabel('Rank', { exact: true }).selectOption('Sergeant');
  // Inject a transport outage, not a successful mock: confirmed state must survive.
  await page.route('**/api/backend/profile', route => route.abort());
  await page.getByRole('button', { name: 'Confirm profile', exact: true }).click();
  await expect(page.getByRole('main').getByRole('alert')).toContainText('confirmed profile has not been changed');
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'Home', exact: true }).click();
  await expect(page.getByText('Warrant Officer Class 1 · Royal Navy', { exact: true })).toBeVisible();
  await expect(page.locator('body')).not.toContainText(process.env.FHQ_API_TOKEN || 'test-only-api-credential-with-32-plus-characters');
});

test('API proxy enforces authentication, origin and endpoint boundaries', async ({ page, baseURL }) => {
  // Node fetch has no inherited Playwright project's httpCredentials.
  const anonymous = await fetch(new URL('/api/backend/profile/options', baseURL));
  expect(anonymous.status).toBe(401);
  await page.goto('/');
  const results = await page.evaluate(async () => {
    const unauthorisedPath = await fetch('/api/backend/policy_data/manifest.json');
    const rejectedOrigin = await fetch('/api/backend/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    return { path: unauthorisedPath.status, empty: rejectedOrigin.status, cache: rejectedOrigin.headers.get('cache-control') };
  });
  expect(results.path).toBe(404); expect(results.empty).toBe(422); expect(results.cache).toContain('no-store');
  const crossOrigin = await page.request.put('/api/backend/profile', { headers: { Origin: 'https://untrusted.invalid' }, data: {} });
  expect(crossOrigin.status()).toBe(403);
});
