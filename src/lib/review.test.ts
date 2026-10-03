import { describe, expect, it } from 'vitest';
import type { Profile } from '@/data/schema';
import { cand, ev, q } from '@/test/fixtures';
import { generateReview, optionState, parseElection, parseVote, quizCandidates, VOTE_OPTIONS } from './review';
import { buildCatalog } from './subjects';

const src = { url: 'https://example.org', accessed: '2026-10-03', label: 'TSE, histórico de candidaturas 2026' };
const claim = (text: string) => ({ text, support: text, source: src, checkId: text });

const candidates = [
  cand('presidente-13', { ballotName: 'LULA' }),
  cand('presidente-22', { ballotName: 'FLAVIO BOLSONARO' }),
  cand('presidente-55', { ballotName: 'RONALDO CAIADO' }),
  cand('presidente-30', { ballotName: 'ZEMA' }),
  cand('presidente-28', { ballotName: 'LEONARDO AVALANCHE', withdrawn: true }),
  cand('senador-155', { ballotName: 'VENEZIANO' }),
  cand('deputado_federal-1111', { ballotName: 'AGUINALDO RIBEIRO' }),
];
const catalog = buildCatalog(candidates);

const profile = (candidateId: string, office: Profile['office'], experience: string[] = []): Profile => ({
  candidateId,
  office,
  pollRank: 1,
  presents: [],
  experience: experience.map(claim),
  proposals: [],
  defends: [],
});

const profiles = [
  profile('presidente-13', 'presidente', ['2022: eleição para presidente (BR), pelo PT. Resultado no TSE: Eleito.']),
  profile('presidente-22', 'presidente', ['2018: eleição para senador (RJ), pelo PSL. Resultado no TSE: Eleito.']),
  profile('presidente-55', 'presidente'),
  profile('presidente-30', 'presidente'),
  profile('presidente-28', 'presidente'),
  profile('deputado_federal-1111', 'deputado_federal'),
];

const questions = [q('eco-privatizacao', { statement: 'Empresas estatais como a Eletrobras devem ser privatizadas.' })];

describe('parseVote', () => {
  it('splits the bill code, its plain-language topic and where it was voted', () => {
    expect(parseVote('Votou SIM na MP 1.031/2021 (privatização da Eletrobras) na Câmara, 19/05/2021 (então no DEM).')).toEqual({
      vote: 'SIM',
      code: 'MP 1.031/2021',
      topic: 'privatização da Eletrobras',
      where: 'na Câmara, 19/05/2021',
    });
    expect(parseVote('Votou NÃO na PEC 45/2019 (reforma tributária), 2º turno no Senado, 08/11/2023 (então no PL).')?.where).toBe('2º turno no Senado, 08/11/2023');
    expect(parseVote('Sancionou a Lei 14.723/2023.')).toBeNull();
  });
});

describe('parseElection', () => {
  it('reads year, office and place from a TSE history line', () => {
    expect(parseElection('2018: eleição para senador (RJ), pelo PSL. Resultado no TSE: Eleito.')).toEqual({ year: '2018', office: 'senador', place: 'RJ' });
    expect(parseElection('Posse como presidente em 2003.')).toBeNull();
  });
});

describe('quizCandidates', () => {
  it('keeps profiled majoritarian candidates who are still running', () => {
    expect([...quizCandidates(profiles, catalog)].sort()).toEqual(['presidente-13', 'presidente-22', 'presidente-30', 'presidente-55']);
  });
});

describe('generateReview', () => {
  const evidence = [
    ev('presidente-22', 'eco-privatizacao', { detail: 'Votou SIM na MP 1.031/2021 (privatização da Eletrobras) no Senado, 16/06/2021 (então no PATRIOTA).', position: 1 }),
    ev('senador-155', 'eco-privatizacao', { detail: 'Votou NÃO na MP 1.031/2021 (privatização da Eletrobras) no Senado, 16/06/2021.', position: -1 }),
    ev('presidente-22', 'eco-privatizacao', { lowDiscrimination: true }),
    ev('presidente-13', 'eco-privatizacao', {
      kind: 'platform',
      quote: 'Vamos manter a Petrobras pública.',
      detail: 'O plano de governo registrado no TSE defende manter estatais.',
      source: { url: 'u', accessed: 'a', label: 'Plano de governo registrado no TSE, p. 3' },
    }),
  ];
  const cards = generateReview({ evidence, catalog, profiles, questions, seed: 5, limit: 20 });

  it('asks about votes in plain language with the bill reference in parentheses, only for quiz candidates', () => {
    const votes = cards.filter((c) => c.kind === 'vote');
    expect(votes).toHaveLength(1);
    expect(votes[0]?.prompt).toBe('Na votação sobre privatização da Eletrobras (MP 1.031/2021, no Senado, 16/06/2021), como Flavio Bolsonaro votou?');
    expect(votes[0]?.options).toEqual(VOTE_OPTIONS);
    expect(votes[0]?.options[votes[0].correct]?.label).toBe('A favor (votou SIM)');
    expect(votes[0]?.explanation).toContain('esse voto conta como a favor');
  });

  it('builds a plan-quote card with three same-office options, one right', () => {
    const quote = cards.find((c) => c.kind === 'quote');
    expect(quote?.prompt).toBe('Quem escreveu isto no plano de governo?');
    expect(quote?.options).toHaveLength(3);
    expect(quote?.options[quote.correct]?.candidateId).toBe('presidente-13');
    expect(quote?.options.some((o) => o.candidateId === 'presidente-28')).toBe(false);
  });

  it('builds fact cards from the TSE election history', () => {
    const fact = cards.find((c) => c.kind === 'fact' && c.candidateId === 'presidente-22');
    expect(fact?.prompt).toBe('Quem foi eleito para senador (RJ) em 2018?');
    expect(fact?.options[fact.correct]?.label).toBe('Flavio Bolsonaro');
    expect(fact?.source.label).toBe('TSE, histórico de candidaturas 2026');
  });

  it('never shows withdrawn or non-quiz candidates', () => {
    const ids = cards.flatMap((c) => [c.candidateId, ...c.options.map((o) => o.candidateId)]).filter(Boolean);
    expect(ids).not.toContain('presidente-28');
    expect(ids).not.toContain('senador-155');
    expect(ids).not.toContain('deputado_federal-1111');
  });

  it('is deterministic for a seed and respects the limit', () => {
    const a = generateReview({ evidence, catalog, profiles, questions, seed: 3, limit: 2 });
    const b = generateReview({ evidence, catalog, profiles, questions, seed: 3, limit: 2 });
    expect(a).toHaveLength(2);
    expect(a.map((c) => c.id)).toEqual(b.map((c) => c.id));
  });
});

describe('optionState', () => {
  it('marks the right answer and the wrong pick after answering', () => {
    expect(optionState(0, null, 0)).toBe('idle');
    expect(optionState(0, 1, 0)).toBe('right');
    expect(optionState(1, 1, 0)).toBe('wrong');
    expect(optionState(2, 1, 0)).toBe('idle');
  });
});

describe('parseVote party note', () => {
  it('drops any "(então ...)" party note, including "sem partido"', async () => {
    const { parseVote } = await import('./review');
    const v = parseVote('Votou NÃO no PL 2.630/2020, substitutivo no Senado, 30/06/2020 (então sem partido).');
    expect(v?.code).toBe('PL 2.630/2020, substitutivo no Senado, 30/06/2020');
    expect(v?.topic).toBeNull();
  });
});
