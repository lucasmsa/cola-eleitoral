import { describe, expect, it } from 'vitest';
import type { AxisAssignment, CountryStance } from '@/data/schema';
import { ev } from '@/test/fixtures';
import {
  agreementWith,
  answerPositions,
  countryPositions,
  placeOnAxes,
  rankAligned,
  subjectPositions,
  toUnit,
  type AlignedEntity,
} from './alignment';
import type { Answers } from './score';

const axes: AxisAssignment[] = [
  { questionId: 'e1', axis: 'economico', direction: 1, rationale: 'r' },
  { questionId: 'e2', axis: 'economico', direction: -1, rationale: 'r' },
  { questionId: 'e3', axis: 'economico', direction: 1, rationale: 'r' },
  { questionId: 's1', axis: 'social', direction: 1, rationale: 'r' },
  { questionId: 's2', axis: 'social', direction: 1, rationale: 'r' },
  { questionId: 's3', axis: 'social', direction: -1, rationale: 'r' },
];

const weights = { record: 0.8, platform: 0.2 };

describe('placeOnAxes', () => {
  it('shrinks each axis toward the center with 2 neutral pseudo-answers', () => {
    const p = placeOnAxes(new Map([['e1', 1], ['e2', 1], ['e3', 1], ['s1', -1], ['s2', -1], ['s3', 1]]), axes);
    expect(p.x).toEqual({ value: 1 / 5, n: 3 });
    expect(p.y).toEqual({ value: -3 / 5, n: 3 });
    expect(p.visible).toBe(true);
  });

  it('only nears the edge with many consistent positions', () => {
    const many: AxisAssignment[] = Array.from({ length: 10 }, (_, i) => ({ questionId: `m${i}`, axis: 'economico', direction: 1, rationale: 'r' }));
    const p = placeOnAxes(new Map(many.map((a) => [a.questionId, 1])), many);
    expect(p.x.value).toBeCloseTo(10 / 12);
  });

  it('shows a placement with 2 questions per axis and hides it with 1', () => {
    expect(placeOnAxes(new Map([['e1', 1], ['e2', 1], ['s1', 1], ['s2', 1]]), axes).visible).toBe(true);
    const p = placeOnAxes(new Map([['e1', 1], ['e2', 1], ['e3', 1], ['s1', 1]]), axes);
    expect(p.y.n).toBe(1);
    expect(p.visible).toBe(false);
  });
});

describe('positions', () => {
  it('reads the user stances and leaves skipped questions out', () => {
    const answers: Answers = { e1: { stance: 0.5, importance: 1 }, e2: 'skip' };
    expect([...answerPositions(answers)]).toEqual([['e1', 0.5]]);
  });

  it('blends a subject record and platform evidence per question', () => {
    const map = subjectPositions(
      [ev('presidente-13', 'e1', { position: 1 }), ev('presidente-13', 'e1', { kind: 'platform', position: -1 }), ev('presidente-22', 'e1', { position: -1 })],
      { type: 'candidate', id: 'presidente-13' },
      weights,
    );
    expect(map.get('e1')).toBeCloseTo(0.6);
    expect(map.size).toBe(1);
  });

  it('reads one country only', () => {
    const stances: CountryStance[] = [
      { id: 'a', country: 'Uruguai', questionId: 's1', position: -1, detail: '', support: '', source: { url: '', accessed: '', label: '' }, checkId: 'a' },
      { id: 'b', country: 'Chile', questionId: 's1', position: 1, detail: '', support: '', source: { url: '', accessed: '', label: '' }, checkId: 'b' },
    ];
    expect([...countryPositions(stances, 'Uruguai')]).toEqual([['s1', -1]]);
  });
});

describe('agreement', () => {
  const answers: Answers = { e1: { stance: 1, importance: 2 }, e2: { stance: -1, importance: 1 }, s1: 'skip' };

  it('weights agreement by importance over common questions only', () => {
    const a = agreementWith(answers, new Map([['e1', 1], ['e2', 1], ['s1', 1]]));
    expect(a.common).toBe(2);
    expect(a.score).toBeCloseTo((2 * 1 + 1 * 0) / 3);
  });

  it('ranks entities and drops those with too few questions in common', () => {
    const entities: AlignedEntity[] = [
      { id: 'x', label: 'X', detail: '', kind: 'pais', positions: new Map([['e1', -1], ['e2', -1], ['e3', 0]]) },
      { id: 'y', label: 'Y', detail: '', kind: 'pais', positions: new Map([['e1', 1], ['e2', -1], ['e3', 0]]) },
      { id: 'z', label: 'Z', detail: '', kind: 'pais', positions: new Map([['e1', 1]]) },
    ];
    const ranked = rankAligned(entities, { ...answers, e3: { stance: 0, importance: 1 } });
    expect(ranked.map((r) => r.entity.id)).toEqual(['y', 'x']);
  });
});

describe('toUnit', () => {
  it('maps -1..1 onto 0..1 and clamps', () => {
    expect(toUnit(-1)).toBe(0);
    expect(toUnit(0)).toBe(0.5);
    expect(toUnit(3)).toBe(1);
  });
});

describe('answersMissing', () => {
  it('counts how many more answers each axis needs, never negative', async () => {
    const { answersMissing } = await import('./alignment');
    expect(answersMissing(3, { x: 0, y: 2 })).toEqual({ x: 3, y: 1 });
    expect(answersMissing(3, { x: 5, y: 3 })).toEqual({ x: 0, y: 0 });
  });
});
