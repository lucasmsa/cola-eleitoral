import { describe, expect, it } from 'vitest';
import type { Round2 } from '@/data/schema';
import { cand, ev, q } from '@/test/fixtures';
import { activeElection, finalistsOf, firstMissingUnit, headToHead, missingQuestions, round2Candidates, winnerOf } from './round2';
import type { Answers } from './score';

const weights = { record: 0.8, platform: 0.2 };
const src = { url: 'https://resultados.tse.jus.br/x', accessed: '2026-10-05', label: 'TSE' };

const round2: Round2 = {
  date: '2026-10-25',
  dateSource: src,
  offices: [
    {
      office: 'presidente',
      status: 'runoff',
      finalists: [
        { candidateId: 'presidente-22', number: '22', ballotName: 'FLAVIO BOLSONARO', pctBrasil: '47,03', pctParaiba: '33,07' },
        { candidateId: 'presidente-13', number: '13', ballotName: 'LULA', pctBrasil: '45,16', pctParaiba: '61,31' },
      ],
      sources: [src],
    },
    {
      office: 'governador',
      status: 'decided',
      winner: { candidateId: 'governador-11', number: '11', ballotName: 'LUCAS RIBEIRO', pct: '64,30' },
      sources: [src],
    },
  ],
};

const questions = [
  q('a', { offices: ['presidente'] }),
  q('b', { offices: ['presidente'] }),
  q('c', { offices: ['presidente'] }),
  q('pb', { offices: ['governador'] }),
];
const evidence = [
  ev('presidente-22', 'a', { position: 1 }),
  ev('presidente-13', 'a', { position: -1 }),
  ev('presidente-13', 'b', { position: 1 }),
  ev('presidente-30', 'c', { position: 1 }),
];

describe('finalistsOf and winnerOf', () => {
  it('reads the runoff pair and the decided winner', () => {
    expect(finalistsOf(round2, 'presidente').map((f) => f.number)).toEqual(['22', '13']);
    expect(finalistsOf(round2, 'governador')).toEqual([]);
    expect(winnerOf(round2, 'governador')?.ballotName).toBe('LUCAS RIBEIRO');
    expect(winnerOf(round2, 'presidente')).toBeNull();
  });
});

describe('headToHead', () => {
  const answers: Answers = { a: { stance: 1, importance: 1 }, b: { stance: -1, importance: 1 } };
  const h = headToHead(round2, 'presidente', questions, evidence, answers, weights);

  it('keeps only questions where at least one finalist has checked evidence', () => {
    expect(h.rows.map((r) => r.question.id)).toEqual(['a', 'b']);
  });

  it('marks a finalist without evidence on a question as missing', () => {
    const b = h.rows.find((r) => r.question.id === 'b')!;
    expect(b.sides['presidente-22']!.position).toBeNull();
    expect(b.sides['presidente-13']!.position).toBe(1);
  });

  it('scores each finalist with the shared model', () => {
    expect(h.scores['presidente-22']!.score).toBe(1);
    expect(h.scores['presidente-13']!.score).toBe(0);
    expect(h.scores['presidente-22']!.coverage).toBeCloseTo(0.5);
  });

  it('puts questions both finalists answered first', () => {
    expect(h.rows[0]!.question.id).toBe('a');
  });
});

describe('missingQuestions and firstMissingUnit', () => {
  it('lists relevant questions the user has not answered, both-evidence ones first', () => {
    const h = headToHead(round2, 'presidente', questions, evidence, { b: 'skip' }, weights);
    expect(missingQuestions(h, { b: 'skip' }).map((x) => x.id)).toEqual(['a']);
  });

  it('finds the lesson unit holding the first missing question', () => {
    const units = [
      { id: 'economia', label: 'E', blurb: '', questions: [questions[1]!] },
      { id: 'social', label: 'S', blurb: '', questions: [questions[0]!] },
    ];
    expect(firstMissingUnit(units, [questions[0]!])).toBe('social');
    expect(firstMissingUnit(units, [])).toBeNull();
  });
});

describe('round2Candidates', () => {
  it('only accepts the two finalists in the 2nd-round cola', () => {
    const all = [cand('presidente-22'), cand('presidente-13'), cand('presidente-30')];
    expect(round2Candidates(round2, all).map((c) => c.id)).toEqual(['presidente-22', 'presidente-13']);
  });
});

describe('activeElection', () => {
  it('points at the 1st round until it passes, then at the runoff', () => {
    expect(activeElection('2026-10-04', '2026-10-04', '2026-10-25').round).toBe(1);
    expect(activeElection('2026-10-05', '2026-10-04', '2026-10-25')).toEqual({ round: 2, date: '2026-10-25', days: 20 });
  });
});

describe('finalistCoverage', () => {
  it('counts answered questions where the finalist has a checked position', async () => {
    const { finalistCoverage } = await import('./round2');
    const answers: Answers = { a: { stance: 1, importance: 1 }, b: { stance: -1, importance: 1 }, c: 'skip' };
    const h = headToHead(round2, 'presidente', questions, evidence, answers, weights);
    expect(finalistCoverage(h, answers, 'presidente-22')).toEqual({ covered: 1, answered: 2 });
    expect(finalistCoverage(h, answers, 'presidente-13')).toEqual({ covered: 2, answered: 2 });
  });
});
