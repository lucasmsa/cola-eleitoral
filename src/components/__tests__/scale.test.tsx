import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { StanceOptions } from '../lesson/StanceOptions';

describe('StanceOptions with a question scale', () => {
  it('shows the labelled positions and reports the mapped stance number', async () => {
    const onSelect = vi.fn();
    render(
      <StanceOptions
        options={[
          { value: -1, label: 'Restringir mais' },
          { value: 0, label: 'Manter as regras atuais' },
          { value: 1, label: 'Ampliar o acesso a armas' },
        ]}
        selected={null}
        onSelect={onSelect}
      />,
    );
    expect(screen.queryByRole('radio', { name: 'Concordo' })).not.toBeInTheDocument();
    await userEvent.setup().click(screen.getByRole('radio', { name: 'Manter as regras atuais' }));
    expect(onSelect).toHaveBeenCalledWith(0);
  });
});
