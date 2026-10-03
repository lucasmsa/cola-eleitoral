import { describe, expect, it } from 'vitest';
import { brDate, brNumber, hostname, percent, pollValue } from './text';

describe('text helpers', () => {
  it('formats Brazilian dates, decimals and percents', () => {
    expect(brDate('2026-10-04')).toBe('04/10/2026');
    expect(brNumber(45.3)).toBe('45,3');
    expect(percent(0.756)).toBe('76%');
  });
  it('shows a zero poll value the way the source writes it', () => {
    expect(pollValue(0)).toBe('não pontuou');
    expect(pollValue(2)).toBe('2%');
  });
  it('reduces a source URL to its host', () => {
    expect(hostname('https://www.poder360.com.br/x/y')).toBe('poder360.com.br');
  });
});
