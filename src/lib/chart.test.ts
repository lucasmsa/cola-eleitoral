import { describe, expect, it } from 'vitest';
import type { AxisAssignment } from '@/data/schema';
import { CHART, plotDots } from './chart';

const axes: AxisAssignment[] = ['e1', 'e2', 'e3'].map((questionId) => ({ questionId, axis: 'economico', direction: 1, rationale: '' }))
  .concat(['s1', 's2', 's3'].map((questionId) => ({ questionId, axis: 'social', direction: 1, rationale: '' }))) as AxisAssignment[];

const full = new Map(['e1', 'e2', 'e3', 's1', 's2', 's3'].map((q) => [q, 1]));

describe('plotDots', () => {
  it('puts "mais mercado" right and "conservador" on top, shrunk toward the center', () => {
    const { dots } = plotDots([{ id: 'a', label: 'A', detail: '', kind: 'pais', positions: full }], axes);
    const span = CHART.size - 2 * CHART.pad;
    expect(dots[0]?.cx).toBeCloseTo(CHART.pad + 0.8 * span);
    expect(dots[0]?.cy).toBeCloseTo(CHART.pad + 0.2 * span);
  });

  it('puts the label on the left of a dot near the right edge so it is not clipped', () => {
    const many = ['economico', 'social'].flatMap((axis) =>
      Array.from({ length: 12 }, (_, i) => ({ questionId: `${axis}${i}`, axis, direction: 1, rationale: '' })),
    ) as AxisAssignment[];
    const right = new Map(many.map((a) => [a.questionId, 1]));
    const { dots } = plotDots(
      [
        { id: 'r', label: 'Flavio Bolsonaro', detail: '', kind: 'politico', positions: right },
        { id: 'l', label: 'Lula', detail: '', kind: 'politico', positions: new Map([...right].map(([k]) => [k, -1])) },
      ],
      many,
    );
    expect(dots.find((d) => d.id === 'r')?.labelSide).toBe('left');
    expect(dots.find((d) => d.id === 'l')?.labelSide).toBe('right');
  });

  it('keeps entities with too few questions out of the drawing', () => {
    const { dots, hidden } = plotDots([{ id: 'b', label: 'B', detail: '', kind: 'pais', positions: new Map([['e1', 1]]) }], axes);
    expect(dots).toHaveLength(0);
    expect(hidden.map((h) => h.id)).toEqual(['b']);
  });
});
