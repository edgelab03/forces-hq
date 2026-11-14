import { defineConfig } from '@playwright/test';
import { existsSync } from 'node:fs';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  workers: 3,
  timeout: 30_000,
  reporter: 'list',
  use: {
    baseURL: process.env.APP_URL || 'http://127.0.0.1:3000',
    browserName: 'chromium',
    launchOptions: { executablePath: process.env.CHROMIUM_PATH || (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined), args: ['--no-sandbox'] },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [360, 390, 412].map(width => ({
    name: `mobile-${width}`,
    use: { viewport: { width, height: width === 360 ? 800 : width === 390 ? 844 : 915 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 },
  })),
});
