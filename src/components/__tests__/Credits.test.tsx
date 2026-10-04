import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Credits } from '../shell/Credits';

describe('Credits', () => {
  it('links to the GitHub profile, the source and a correction e-mail, with no donation link', () => {
    render(<Credits />);
    expect(screen.getByRole('link', { name: 'feito por lucasmsa' })).toHaveAttribute('href', 'https://github.com/lucasmsa');
    expect(screen.getByRole('link', { name: 'código-fonte' })).toHaveAttribute('href', 'https://github.com/lucasmsa/cola-eleitoral');
    expect(screen.getByRole('link', { name: 'lucasmsea@outlook.com' })).toHaveAttribute('href', 'mailto:lucasmsea@outlook.com');
    expect(screen.getByText(/sem vínculo com candidatos, partidos ou federações/)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /café/ })).not.toBeInTheDocument();
  });
});
