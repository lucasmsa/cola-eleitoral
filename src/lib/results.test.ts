import { describe, expect, it } from 'vitest';
import { cand, ev, q } from '@/test/fixtures';
import { rankCandidates, rankLists } from './results';

const weights = { record: 0.8, platform: 0.2 };
const candidates = [
  cand('senador-100', { list: 'A' }),
  cand('senador-155', { list: 'B' }),
  cand('senador-400', { list: 'B' }),
  cand('presidente-13'),
];
const questions = [q('q1', { offices: ['senador'] }), q('q2', { offices: ['presidente'] })];

describe('rankCandidates', () => {
  it('ranks only the office and only questions that apply to it', () => {
    const r = rankCandidates(
      'senador',
      candidates,
      questions,
      [ev('senador-155', 'q1'), ev('senador-100', 'q1', { position: -1 }), ev('senador-100', 'q2')],
      { q1: { stance: 1, importance: 1 }, q2: { stance: 1, importance: 1 } },
      weights,
    );
    expect(r.answered).toBe(1);
    expect(r.scored.map((s) => s.subjectId)).toEqual(['senador-155', 'senador-100']);
    expect(r.unscored.map((s) => s.subjectId)).toEqual(['senador-400']);
  });

  it('leaves withdrawn candidates out of the ranking', () => {
    const withWithdrawn = [...candidates, cand('senador-272', { withdrawn: true })];
    const r = rankCandidates('senador', withWithdrawn, questions, [ev('senador-272', 'q1')], { q1: { stance: 1, importance: 1 } }, weights);
    expect([...r.scored, ...r.unscored].map((s) => s.subjectId)).not.toContain('senador-272');
  });

  it('can restrict to one list', () => {
    const r = rankCandidates('senador', candidates, questions, [], {}, weights, 'B');
    expect(r.unscored.map((s) => s.subjectId).sort()).toEqual(['senador-155', 'senador-400']);
  });
});

describe('rankLists', () => {
  it('scores lists of the office from list evidence on every answered question', () => {
    const r = rankLists(
      'senador',
      candidates,
      [ev('A', 'q2', { subject: { type: 'list', id: 'A' } })],
      { q2: { stance: 1, importance: 1 } },
      weights,
    );
    expect(r.scored.map((s) => s.subjectId)).toEqual(['A']);
    expect(r.unscored.map((s) => s.subjectId)).toEqual(['B']);
  });
});

describe('labels', () => {
  it('names how much of a score comes from records', async () => {
    const { measuredLabel } = await import('./results');
    expect(measuredLabel(1)).toBe('medido');
    expect(measuredLabel(0)).toBe('declarado, não medido');
    expect(measuredLabel(0.6)).toBe('60% medido');
  });

  it('counts answered questions that have evidence for the subject', async () => {
    const { coveredCount } = await import('./results');
    const n = coveredCount(
      { type: 'candidate', id: 'senador-155' },
      { q1: { stance: 1, importance: 2 }, q2: 'skip', q3: { stance: 0, importance: 1 } },
      [ev('senador-155', 'q1'), ev('senador-155', 'q2'), ev('senador-100', 'q3')],
    );
    expect(n).toBe(1);
  });
});

describe('isThinEvidence', () => {
  it('flags coverage under 40% of answered questions', async () => {
    const { isThinEvidence } = await import('./results');
    expect(isThinEvidence(1, 5)).toBe(true);
    expect(isThinEvidence(2, 5)).toBe(false);
    expect(isThinEvidence(0, 0)).toBe(false);
  });
});
