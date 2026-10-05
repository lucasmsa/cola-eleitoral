import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { Credits } from '../shell/Credits';

describe('Credits', () => {
  afterEach(() => vi.useRealTimers());

  it('credits the author site, the source and the coffee page', () => {
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date('2026-10-05T15:00:00Z'));
    render(<Credits />);
    const github = screen.getByRole('link', { name: 'feito por lucasmsa' });
    const coffee = screen.getByRole('link', { name: 'me paga um café ☕' });
    expect(github).toHaveAttribute('href', 'https://lucasmsa.com');
    expect(github.getAttribute('rel')).toContain('author');
    expect(coffee).toHaveAttribute('href', 'https://buymeacoffee.com/lmsamoreirt');
    expect(coffee).toHaveAttribute('target', '_blank');
    expect(screen.getByRole('link', { name: 'código-fonte' })).toHaveAttribute('href', 'https://github.com/lucasmsa/cola-eleitoral');
  });

  it('hides the coffee link on election day in São Paulo', () => {
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date('2026-10-25T13:00:00Z'));
    render(<Credits />);
    expect(screen.queryByRole('link', { name: 'me paga um café ☕' })).toBeNull();
    expect(screen.getByRole('link', { name: 'feito por lucasmsa' })).toBeInTheDocument();
  });
});
