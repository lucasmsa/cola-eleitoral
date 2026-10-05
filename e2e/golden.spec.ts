import { expect, test } from '@playwright/test';

test('answer three questions, see the result sequence, put a senator in the cola, restart', async ({ page }) => {
  const hosts = new Set<string>();
  page.on('request', (r) => hosts.add(new URL(r.url()).host));
  await page.goto('/');
  await expect.poll(() => page.evaluate(() => document.fonts.check("700 20px 'Kalam'", 'Falta é ção'))).toBe(true);
  await page.getByRole('button', { name: 'Começar: Economia' }).click();

  await expect(page.getByText('Entenda antes de responder')).toBeVisible();
  for (const pick of [3, 0, 4]) {
    await page.getByRole('radiogroup', { name: 'Sua posição' }).getByRole('radio').nth(pick).click();
    await page.getByRole('button', { name: 'Confirmar' }).click();
    await expect(page.getByText('Resposta registrada.')).toBeVisible();
    await expect(page.getByText(/Votou (SIM|NÃO)/)).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Confirmar' })).toBeVisible({ timeout: 5000 });
  }

  await page.getByRole('button', { name: 'Sair da lição' }).click();
  await expect(page.getByText(/^3 de \d+ perguntas/)).toBeVisible();

  await page.locator('nav').getByRole('button', { name: 'Resultado' }).click();
  await expect(page.getByRole('heading', { name: 'Seu resultado' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Mais alinhados com você' })).toBeVisible();

  await page.getByRole('button', { name: /Senado \(2 votos\)/ }).first().click();
  await expect(page.getByRole('heading', { name: 'Conheça os 5 principais' })).toBeVisible();
  const firstPick = page.getByRole('button', { name: /^Pôr na cola: / }).first();
  const name = ((await firstPick.getAttribute('aria-label')) ?? '').replace('Pôr na cola: ', '');
  await firstPick.click();
  await expect(page.getByText('Na cola (Senador, 1ª vaga)')).toBeVisible();

  await page.locator('nav').getByRole('button', { name: 'Cola' }).click();
  const slot = page.getByLabel('Senador, 1ª vaga');
  await expect(slot).toHaveValue(/^\d{3}$/);
  const digits = await slot.inputValue();
  const card = page.getByTestId('cola-card').first();
  await expect(card).toContainText(name);
  for (const d of digits) await expect(card).toContainText(d);

  await page.reload();
  await page.locator('nav').getByRole('button', { name: 'Cola' }).click();
  await expect(page.getByLabel('Senador, 1ª vaga')).toHaveValue(digits);

  await page.locator('nav').getByRole('button', { name: 'Quiz' }).click();
  await expect(page.getByRole('heading', { name: 'Quiz: quem defende o quê' })).toBeVisible();
  await page.getByRole('button', { name: 'Começar o quiz' }).click();
  await page.getByRole('group', { name: 'Opções' }).getByRole('button').first().click();
  await expect(page.getByText(/Isso mesmo\.|Não foi isso\./)).toBeVisible();
  await expect(page.getByText(/^Fonte:/).first()).toBeVisible();

  await page.getByRole('banner').getByRole('button', { name: 'Início' }).first().click();
  await page.getByRole('button', { name: 'Recomeçar o quiz do zero' }).click();
  await page.getByRole('button', { name: 'Sim, apagar e recomeçar' }).click();
  await expect(page.getByText(/^0 de \d+ perguntas/).first()).toBeVisible();
  await page.locator('nav').getByRole('button', { name: 'Cola' }).click();
  await expect(page.getByLabel('Senador, 1ª vaga')).toHaveValue('');
  expect([...hosts]).toEqual([new URL(page.url()).host]);
});
