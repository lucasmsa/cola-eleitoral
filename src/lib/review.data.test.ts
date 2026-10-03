import { describe, expect, it } from 'vitest';
import { candidates, evidence, profiles, questions } from '@/data';
import { generateReview, quizCandidates } from './review';
import { buildCatalog } from './subjects';

describe('quiz on the shipped data', () => {
  const catalog = buildCatalog(candidates);
  const allowed = quizCandidates(profiles, catalog);
  const cards = [1, 2, 3, 4, 5].flatMap((seed) => generateReview({ evidence, catalog, profiles, questions, seed, limit: 10 }));

  it('builds a full round mixing the three kinds', () => {
    expect(generateReview({ evidence, catalog, profiles, questions, seed: 1, limit: 10 })).toHaveLength(10);
    expect(new Set(cards.map((c) => c.kind))).toEqual(new Set(['vote', 'quote', 'fact']));
  });

  it('never repeats a question within a round', () => {
    for (const seed of [1, 2, 3, 4, 5]) {
      const round = generateReview({ evidence, catalog, profiles, questions, seed, limit: 10 });
      expect(new Set(round.map((c) => `${c.prompt}|${c.quote ?? ''}`)).size).toBe(round.length);
    }
  });

  it('only names quiz candidates and never puts a bill code first', () => {
    for (const c of cards) {
      for (const o of c.options) if (o.candidateId) expect(allowed.has(o.candidateId)).toBe(true);
      expect(c.prompt).not.toMatch(/^(Na votação sobre )?(PEC|PL|PLP|MP|PDL) \d/);
    }
  });
});
