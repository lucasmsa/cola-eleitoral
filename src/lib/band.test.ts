import { describe, expect, it } from 'vitest';
import { bandGeometry } from './band';

describe('bandGeometry', () => {
  it('maps the low/high band and the point to percentages', () => {
    expect(bandGeometry({ subjectId: 'a', score: 0.75, low: 0.5, high: 0.9, coverage: 0.6, measuredShare: 1 })).toEqual({
      left: '50%',
      width: '40%',
      point: '75%',
    });
  });
  it('has no point when there is no score', () => {
    expect(bandGeometry({ subjectId: 'a', score: null, low: 0, high: 1, coverage: 0, measuredShare: 0 }).point).toBeNull();
  });
});
