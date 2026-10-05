import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { DataInfo } from '../shell/DataInfo';

describe('DataInfo', () => {
  it('opens on click, shows the caveat, and closes on Escape returning focus', async () => {
    const user = userEvent.setup();
    render(
      <DataInfo>
        <p>fonte</p>
      </DataInfo>,
    );
    const button = screen.getByRole('button', { name: 'Sobre os dados' });
    expect(button).toHaveAttribute('aria-expanded', 'false');
    await user.click(button);
    expect(button).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByText(/decisões judiciais, renúncias e novas pesquisas posteriores/)).toBeInTheDocument();
    expect(screen.getByText('Resultados (TSE)')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(button).toHaveAttribute('aria-expanded', 'false');
    expect(button).toHaveFocus();
  });

  it('opens with the keyboard', async () => {
    const user = userEvent.setup();
    render(
      <DataInfo>
        <p>fonte</p>
      </DataInfo>,
    );
    await user.tab();
    await user.keyboard('{Enter}');
    expect(screen.getByRole('region', { name: 'Sobre os dados' })).toBeInTheDocument();
  });
});
