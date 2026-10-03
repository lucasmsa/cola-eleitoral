import { describe, expect, it } from 'vitest';
import type { Claim, Explainer } from '@/data/schema';
import { explainerFor, explainerSections } from './explainers';

const claim = (text: string): Claim => ({ text, support: text, source: { url: 'u', accessed: 'a', label: 'Fonte' }, checkId: text });

const ex: Explainer = {
  questionId: 'q1',
  whatItIs: [claim('Definição.')],
  inPractice: [],
  argsFor: [claim('A favor.')],
  argsAgainst: [claim('Contra.')],
  nuance: [],
};

describe('explainers', () => {
  it('finds the explainer of a question', () => {
    expect(explainerFor([ex], 'q1')).toBe(ex);
    expect(explainerFor([ex], 'q2')).toBeNull();
  });

  it('keeps only sections with claims, in reading order', () => {
    expect(explainerSections(ex).map((s) => s.title)).toEqual(['O que é', 'Quem defende argumenta', 'Quem critica argumenta']);
    expect(explainerSections(null)).toEqual([]);
  });
});
