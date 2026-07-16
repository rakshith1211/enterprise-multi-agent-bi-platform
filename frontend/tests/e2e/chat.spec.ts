import { test, expect } from '@playwright/test'

test('should render platform title', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('Enterprise Multi-Agent BI Platform')
})
