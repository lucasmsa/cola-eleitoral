import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Credits } from '../shell/Credits';

describe('Credits', () => {
  it('credits the author site, the source and the coffee page', () => {
    render(<Credits />);
    const github = screen.getByRole('link', { name: 'feito por lucasmsa' });
    const coffee = screen.getByRole('link', { name: 'me paga um café ☕' });
    expect(github).toHaveAttribute('href', 'https://lucasmsa.com');
    expect(github.getAttribute('rel')).toContain('author');
    expect(coffee).toHaveAttribute('href', 'https://buymeacoffee.com/lmsamoreirt');
    expect(coffee).toHaveAttribute('target', '_blank');
    expect(screen.getByRole('link', { name: 'código-fonte' })).toHaveAttribute('href', 'https://github.com/lucasmsa/cola-eleitoral');
  });
});
