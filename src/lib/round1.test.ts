import { describe, expect, it } from 'vitest';
import type { MajoritarianResult, ProportionalResult, ResultCandidate, Round1 } from '@/data/schema';
import { barRows, electedByList, formatInt, pickOutcomes } from './round1';

const src = { url: 'https://x', accessed: '2026-10-05', label: 'TSE', generated: '04/10/2026 23:23' };

function c(number: string, office: string, partial: Partial<ResultCandidate> = {}): ResultCandidate {
  return {
    candidateId: `${office}-${number}`,
    number,
    ballotName: `NOME ${number}`,
    party: 'PX',
    list: 'LISTA X',
    votes: 100,
    pct: 10,
    pctLabel: '10,00',
    status: 'Não eleito',
    elected: false,
    ...partial,
  };
}

const maj = (cands: ResultCandidate[], seats = 1): MajoritarianResult => ({ candidates: cands, seatsTotal: seats, source: src });

const prop: ProportionalResult = {
  seatsTotal: 3,
  candidates: [
    c('1111', 'deputado_federal', { list: 'LISTA A', votes: 50, elected: true, status: 'Eleito por QP' }),
    c('1122', 'deputado_federal', { list: 'LISTA A', votes: 90, elected: true, status: 'Eleito por QP' }),
    c('2233', 'deputado_federal', { list: 'LISTA B', votes: 70, elected: true, status: 'Eleito por média' }),
    c('2244', 'deputado_federal', { list: 'LISTA B', votes: 20, status: 'Suplente' }),
  ],
  seats: [
    { list: 'LISTA A', parties: 'AA', seats: 2 },
    { list: 'LISTA B', parties: 'BB', seats: 1 },
  ],
  elected: [
    { ...c('1111', 'deputado_federal', { list: 'LISTA A', votes: 50, elected: true, status: 'Eleito por QP' }), how: 'QP' },
    { ...c('1122', 'deputado_federal', { list: 'LISTA A', votes: 90, elected: true, status: 'Eleito por QP' }), how: 'QP' },
    { ...c('2233', 'deputado_federal', { list: 'LISTA B', votes: 70, elected: true, status: 'Eleito por média' }), how: 'média' },
  ],
  source: src,
};

const round1: Round1 = {
  round: 1,
  date: '2026-10-04',
  presidente: {
    br: maj([c('22', 'presidente', { status: '2º turno', pct: 47 }), c('13', 'presidente', { status: '2º turno', pct: 45 }), c('70', 'presidente')]),
    pb: maj([]),
  },
  governador: maj([c('11', 'governador', { status: 'Eleito', elected: true }), c('22', 'governador')]),
  senador: maj([c('400', 'senador', { status: 'Eleito', elected: true }), c('155', 'senador', { status: 'Eleito', elected: true }), c('100', 'senador')], 2),
  deputadoFederal: prop,
  deputadoEstadual: { ...prop, elected: [], seats: [], candidates: [] },
};

describe('formatInt', () => {
  it('uses pt-BR thousands separators', () => {
    expect(formatInt(1470252)).toBe('1.470.252');
  });
});

describe('barRows', () => {
  it('keeps the vote order, scales to the top share and flags highlighted candidates', () => {
    const rows = barRows(round1.presidente.br, ['presidente-13', 'presidente-22']);
    expect(rows.map((r) => r.number)).toEqual(['22', '13', '70']);
    expect(rows[0]?.width).toBe(1);
    expect(rows[1]?.width).toBeCloseTo(45 / 47);
    expect(rows.map((r) => r.highlight)).toEqual([true, true, false]);
  });
});

describe('electedByList', () => {
  it('groups the elected by list, lists by seats, people by votes', () => {
    const groups = electedByList(prop);
    expect(groups.map((g) => [g.list, g.seats])).toEqual([
      ['LISTA A', 2],
      ['LISTA B', 1],
    ]);
    expect(groups[0]?.people.map((p) => p.number)).toEqual(['1122', '1111']);
  });
});

describe('pickOutcomes', () => {
  it('reports each 1st-round cola pick against the official result', () => {
    const out = pickOutcomes(
      {
        presidente: { kind: 'number', digits: '13' },
        governador: { kind: 'number', digits: '22' },
        senador_1: { kind: 'number', digits: '400' },
        deputado_federal: { kind: 'number', digits: '22' },
        deputado_estadual: { kind: 'branco' },
      },
      round1,
    );
    const by = Object.fromEntries(out.map((o) => [o.slot, o.outcome]));
    expect(by.presidente).toBe('segundo-turno');
    expect(by.governador).toBe('nao-eleito');
    expect(by.senador_1).toBe('eleito');
    expect(by.deputado_federal).toBe('legenda');
    expect(by.deputado_estadual).toBe('branco');
    expect(out.find((o) => o.slot === 'deputado_federal')?.detail).toBe('LISTA B: 1 vaga');
    expect(out.find((o) => o.slot === 'senador_2')).toBeUndefined();
  });

  it('uses the official status for deputados who were not elected', () => {
    const out = pickOutcomes({ deputado_federal: { kind: 'number', digits: '2244' } }, round1);
    expect(out[0]?.outcome).toBe('suplente');
  });

  it('marks a number missing from the results as not found', () => {
    const out = pickOutcomes({ governador: { kind: 'number', digits: '99' } }, round1);
    expect(out[0]?.outcome).toBe('nao-encontrado');
  });
});
