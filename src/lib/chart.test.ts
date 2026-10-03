import { describe, expect, it } from 'vitest';
import type { AxisAssignment } from '@/data/schema';
import { CHART, plotDots } from './chart';

const axes: AxisAssignment[] = ['e1', 'e2', 'e3'].map((questionId) => ({ questionId, axis: 'economico', direction: 1, rationale: '' }))
  .concat(['s1', 's2', 's3'].map((questionId) => ({ questionId, axis: 'social', direction: 1, rationale: '' }))) as AxisAssignment[];

const full = new Map(['e1', 'e2', 'e3', 's1', 's2', 's3'].map((q) => [q, 1]));

describe('plotDots', () => {
  it('puts "mais mercado" right and "conservador" on top', () => {
    const { dots } = plotDots([{ id: 'a', label: 'A', detail: '', kind: 'pais', positions: full }], axes);
    expect(dots[0]?.cx).toBe(CHART.size - CHART.pad);
    expect(dots[0]?.cy).toBe(CHART.pad);
  });

  it('puts the label on the left of a dot near the right edge so it is not clipped', () => {
    const { dots } = plotDots(
      [
        { id: 'r', label: 'Flavio Bolsonaro', detail: '', kind: 'politico', positions: full },
        { id: 'l', label: 'Lula', detail: '', kind: 'politico', positions: new Map([...full].map(([k]) => [k, -1])) },
      ],
      axes,
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
