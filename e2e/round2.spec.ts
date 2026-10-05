import { expect, test } from '@playwright/test';

test('answer 3 questions, compare the runoff finalists, fill the 2nd-round cola', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Flavio Bolsonaro x Lula' }).first()).toBeVisible();
  await expect(page.getByText(/Governador da Paraíba decidido no 1º turno: Lucas Ribeiro, eleito com 64,30%/).first()).toBeVisible();

  await page.getByRole('button', { name: 'Começar: Economia' }).click();
  for (let i = 0; i < 3; i += 1) {
    await page.getByRole('radiogroup', { name: 'Sua posição' }).getByRole('radio').first().click();
    await page.getByRole('button', { name: 'Confirmar' }).click();
    await expect(page.getByText('Resposta registrada.')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Confirmar' })).toBeVisible({ timeout: 5000 });
  }
  await page.getByRole('button', { name: 'Sair da lição' }).click();

  await page.locator('nav').getByRole('button', { name: '2º turno' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Flavio Bolsonaro x Lula' })).toBeVisible();
  await expect(page.getByTestId('finalist-22')).toContainText('47,03% dos votos válidos no Brasil');
  await expect(page.getByTestId('finalist-13')).toContainText('61,31% na Paraíba');
  await expect(page.getByRole('heading', { name: 'Pergunta por pergunta' })).toBeVisible();

  const slot = page.getByLabel('Presidente');
  await slot.fill('30');
  await expect(page.getByText('Este número não está no 2º turno. Os números são 13 e 22.')).toBeVisible();
  await slot.fill('13');
  const card = page.getByTestId('cola2-card');
  await expect(card).toContainText('MINHA COLA, 25 DE OUTUBRO');
  await expect(card).toContainText('Lula');
  await expect(card).toContainText('Governador eleito no 1º turno: Lucas Ribeiro');

  await page.reload();
  await page.locator('nav').getByRole('button', { name: '2º turno' }).click();
  await expect(page.getByLabel('Presidente')).toHaveValue('13');
  await page.locator('nav').getByRole('button', { name: 'Cola' }).click();
  await expect(page.getByLabel('Presidente')).toHaveValue('');
});
