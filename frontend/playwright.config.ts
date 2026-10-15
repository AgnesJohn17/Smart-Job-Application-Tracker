import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  expect: { timeout: 12000 },
  retries: process.env.CI ? 1 : 0,
  use: { baseURL: 'http://127.0.0.1:5173', trace: 'retain-on-failure', ...devices['Desktop Chrome'] },
  reporter: process.env.CI ? 'github' : 'list',
});
