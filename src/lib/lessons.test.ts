import { describe, expect, it } from 'vitest';
import { q } from '@/test/fixtures';
import { buildUnits, firstOpenIndex, unitProgress } from './lessons';

describe('buildUnits', () => {
  it('groups national questions by area in the configured order and skips empty areas', () => {
    const units = buildUnits([q('a', { area: 'social' }), q('b', { area: 'economia' }), q('c', { area: 'economia' })]);
    expect(units.map((u) => u.id)).toEqual(['economia', 'social']);
    expect(units[0]?.questions.map((x) => x.id)).toEqual(['b', 'c']);
  });

  it('puts PB questions in their own unit at the end', () => {
    const units = buildUnits([
      q('pb-agua', { area: 'ambiente', offices: ['governador', 'deputado_estadual'] }),
      q('x', { area: 'ambiente' }),
    ]);
    expect(units.map((u) => u.id)).toEqual(['ambiente', 'pb']);
    expect(units[1]?.questions.map((x) => x.id)).toEqual(['pb-agua']);
  });
});

describe('progress', () => {
  const [unit] = buildUnits([q('a'), q('b'), q('c')]);
  it('counts skipped questions as answered', () => {
    expect(unitProgress(unit!, { a: { stance: 1, importance: 1 }, b: 'skip' })).toEqual({ answered: 2, total: 3 });
  });
  it('resumes at the first unanswered question', () => {
    expect(firstOpenIndex(unit!, { a: 'skip' })).toBe(1);
    expect(firstOpenIndex(unit!, { a: 'skip', b: 'skip', c: 'skip' })).toBe(3);
  });
});

describe('unitStatus', () => {
  it('starts, resumes or redoes a unit', async () => {
    const { unitStatus } = await import('./lessons');
    expect(unitStatus(0, 3)).toBe('start');
    expect(unitStatus(1, 3)).toBe('resume');
    expect(unitStatus(3, 3)).toBe('redo');
  });
});
