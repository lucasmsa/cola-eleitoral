import { describe, expect, it } from 'vitest';
import { estimateWidth, layoutLabels } from './chartLabels';

const bounds = { min: 0, max: 640 };

describe('layoutLabels', () => {
  it('keeps a lone label on the right of its dot', () => {
    expect(layoutLabels([{ id: 'a', cx: 100, cy: 100, width: 60 }], bounds)).toEqual([{ id: 'a', side: 'right', dy: 0 }]);
  });

  it('moves a label off a neighbouring dot it would cover', () => {
    const out = layoutLabels(
      [
        { id: 'yuri', cx: 70, cy: 570, width: 110 },
        { id: 'lula', cx: 130, cy: 570, width: 40 },
      ],
      bounds,
    );
    const yuri = out.find((l) => l.id === 'yuri')!;
    expect(yuri.side === 'right' && yuri.dy === 0).toBe(false);
  });

  it('flips to the left at the right edge', () => {
    expect(layoutLabels([{ id: 'r', cx: 620, cy: 100, width: 120 }], bounds)[0]?.side).toBe('left');
  });

  it('steps around fixed obstacles such as the pole labels', () => {
    const out = layoutLabels([{ id: 'a', cx: 70, cy: 570, width: 110 }], bounds, [{ x: 70, y: 560, w: 200, h: 24 }]);
    expect(out[0]).not.toEqual({ id: 'a', side: 'right', dy: 0 });
  });

  it('estimates width from the label length', () => {
    expect(estimateWidth('Lula')).toBeCloseTo(34.4);
  });
});
