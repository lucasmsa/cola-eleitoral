import { describe, expect, it } from 'vitest';
import type { Evidence } from '@/data/schema';
import { blendPosition, rankSubjects, scoreSubject, type Answers } from './score';

const src = { url: 'https://example.org', accessed: '2026-09-30', label: 'x' };

function ev(
  subjectId: string,
  questionId: string,
  kind: Evidence['kind'],
  position: Evidence['position'],
  type: 'candidate' | 'list' = 'candidate',
): Evidence {
  return {
    id: `${subjectId}:${questionId}:${kind}:${position}`,
    subject: { type, id: subjectId },
    questionId,
    kind,
    position,
    detail: 'd',
    date: '2025-01-01',
    source: src,
    checkId: 'c',
    lowDiscrimination: false,
  };
}

const weights = { record: 0.8, platform: 0.2 };

describe('blendPosition', () => {
  it('weights record 80% and platform 20% when both exist', () => {
    const r = blendPosition([ev('a', 'q', 'record', 1), ev('a', 'q', 'platform', -1)], weights);
    expect(r?.position).toBeCloseTo(0.6);
    expect(r?.measured).toBe(true);
  });

  it('uses platform at 100% and marks it as not measured when there is no record', () => {
    const r = blendPosition([ev('a', 'q', 'platform', -1)], weights);
    expect(r?.position).toBe(-1);
    expect(r?.measured).toBe(false);
  });

  it('averages several votes on the same question', () => {
    const r = blendPosition([ev('a', 'q', 'record', 1), ev('a', 'q', 'record', -1)], weights);
    expect(r?.position).toBe(0);
  });

  it('returns null without evidence', () => {
    expect(blendPosition([], weights)).toBeNull();
  });
});

describe('scoreSubject', () => {
  const answers: Answers = {
    q1: { stance: 1, importance: 2 },
    q2: { stance: -1, importance: 1 },
    q3: { stance: 0.5, importance: 1 },
  };

  it('scores full agreement as 1 and full disagreement as 0', () => {
    const agree = scoreSubject('a', answers, [ev('a', 'q1', 'record', 1), ev('a', 'q2', 'record', -1)], weights);
    expect(agree.score).toBe(1);
    const disagree = scoreSubject('a', answers, [ev('a', 'q1', 'record', -1), ev('a', 'q2', 'record', 1)], weights);
    expect(disagree.score).toBe(0);
  });

  it('weights questions by importance', () => {
    const s = scoreSubject('a', answers, [ev('a', 'q1', 'record', 1), ev('a', 'q2', 'record', 1)], weights);
    expect(s.score).toBeCloseTo((2 * 1 + 1 * 0) / 3);
  });

  it('bounds the score between all-missing-disagree and all-missing-agree', () => {
    const s = scoreSubject('a', answers, [ev('a', 'q1', 'record', 1)], weights);
    expect(s.low).toBeCloseTo(2 / 4);
    expect(s.high).toBeCloseTo(4 / 4);
    expect(s.coverage).toBeCloseTo(2 / 4);
  });

  it('ignores skipped questions and other subjects', () => {
    const s = scoreSubject(
      'a',
      { q1: { stance: 1, importance: 1 }, q2: 'skip' },
      [ev('a', 'q1', 'record', 1), ev('a', 'q2', 'record', 1), ev('b', 'q1', 'record', -1)],
      weights,
    );
    expect(s.score).toBe(1);
    expect(s.coverage).toBe(1);
  });

  it('reports the measured share of covered weight', () => {
    const s = scoreSubject('a', answers, [ev('a', 'q1', 'record', 1), ev('a', 'q2', 'platform', -1)], weights);
    expect(s.measuredShare).toBeCloseTo(2 / 3);
  });

  it('has a null score when nothing answered is covered', () => {
    const s = scoreSubject('a', answers, [], weights);
    expect(s.score).toBeNull();
    expect(s.low).toBe(0);
    expect(s.high).toBe(1);
  });

  it('only counts evidence of the requested subject type', () => {
    const s = scoreSubject('PL', answers, [ev('PL', 'q1', 'record', 1, 'list')], weights, 'list');
    expect(s.score).toBe(1);
    expect(scoreSubject('PL', answers, [ev('PL', 'q1', 'record', 1, 'list')], weights).score).toBeNull();
  });
});

describe('rankSubjects', () => {
  it('orders by score, then coverage, and puts unscored last', () => {
    const answers: Answers = { q1: { stance: 1, importance: 1 }, q2: { stance: 1, importance: 1 } };
    const evidence = [
      ev('a', 'q1', 'record', 1),
      ev('b', 'q1', 'record', 1),
      ev('b', 'q2', 'record', 1),
      ev('c', 'q1', 'record', -1),
    ];
    const ranked = rankSubjects(['d', 'c', 'a', 'b'], answers, evidence, weights);
    expect(ranked.map((r) => r.subjectId)).toEqual(['b', 'a', 'c', 'd']);
  });
});
