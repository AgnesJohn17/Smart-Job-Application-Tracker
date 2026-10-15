import { test, expect } from '@playwright/test';

test('registration, create, search, edit, reload and user isolation', async ({ page }) => {
  const email = 'tester-' + Date.now() + '@example.com';
  await page.goto('/');
  await page.getByRole('button', { name: 'Create account' }).click();
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password').fill('SafeTestPassword123!');
  await page.getByRole('button', { name: 'Create account' }).last().click();
  await expect(page.getByRole('heading', { name: 'Your job search, organized.' })).toBeVisible();

  await page.getByRole('button', { name: 'Add application' }).click();
  await page.getByRole('dialog').getByText('Company *').locator('input').fill('Northstar Software');
  await page.getByRole('dialog').getByText('Role *').locator('input').fill('Software Developer Intern');
  await page.getByRole('dialog').getByText('Status').locator('select').selectOption('Applied');
  await page.getByRole('dialog').getByText('Deadline').locator('input').fill('2027-01-20');
  await page.getByRole('dialog').getByText('Interview date').locator('input').fill('2027-02-03');
  await page.getByRole('button', { name: 'Save application' }).click();
  await expect(page.getByText('Northstar Software')).toBeVisible();
  await expect(page.getByText('Software Developer Intern')).toBeVisible();

  await page.getByLabel('Search applications').fill('unrelated');
  await expect(page.getByText('No applications match your filters.')).toBeVisible();
  await page.getByLabel('Search applications').fill('Northstar');
  await page.getByTitle('Edit').click();
  await page.getByRole('dialog').getByText('Status').locator('select').selectOption('Interview');
  await page.getByRole('button', { name: 'Save application' }).click();
  await expect(page.locator('tbody .pill')).toHaveText('Interview');
  await page.reload();
  await expect(page.getByText('Northstar Software')).toBeVisible();
  await page.getByRole('button', { name: 'Sign out' }).click();

  await page.getByRole('button', { name: 'Create account' }).click();
  await page.getByLabel('Email address').fill('other-' + Date.now() + '@example.com');
  await page.getByLabel('Password').fill('SafeTestPassword123!');
  await page.getByRole('button', { name: 'Create account' }).last().click();
  await expect(page.getByText('No applications yet. Add your first opportunity to get started.')).toBeVisible();
  await expect(page.getByText('Northstar Software')).toHaveCount(0);
});
