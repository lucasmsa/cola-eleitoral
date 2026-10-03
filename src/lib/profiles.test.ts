import { describe, expect, it } from 'vitest';
import type { Profile } from '@/data/schema';
import { cand, ev } from '@/test/fixtures';
import { buildCountries, buildParties, buildPoliticians, chartPoliticians } from './entities';
import { defendsEvidence, firstFilledSection, profilesFor, sectionCounts, vibeLine, visibleSlice } from './profiles';
import { buildCatalog } from './subjects';

const p = (candidateId: string, office: Profile['office'], pollRank: number | null): Profile => ({
  candidateId,
  office,
  pollRank,
  presents: [],
  experience: [],
  proposals: [],
  defends: [],
});

const candidates = [
  cand('governador-11', { list: 'PP' }),
  cand('governador-22', { list: 'PL' }),
  cand('governador-27', { withdrawn: true }),
  cand('deputado_federal-1111', { list: 'PP' }),
  cand('deputado_federal-2222', { list: 'PL' }),
];
const byId = new Map(candidates.map((c) => [c.id, c]));

describe('profilesFor', () => {
  it('orders by poll rank, puts unranked last and drops withdrawn candidates', () => {
    const list = [p('governador-22', 'governador', null), p('governador-27', 'governador', 1), p('governador-11', 'governador', 2)];
    expect(profilesFor(list, 'governador', byId).map((x) => x.candidateId)).toEqual(['governador-11', 'governador-22']);
  });

  it('filters deputados by the chosen list', () => {
    const list = [p('deputado_federal-1111', 'deputado_federal', null), p('deputado_federal-2222', 'deputado_federal', null)];
    expect(profilesFor(list, 'deputado_federal', byId, 'PL').map((x) => x.candidateId)).toEqual(['deputado_federal-2222']);
  });

  it('resolves the evidence a profile cites', () => {
    const e = ev('governador-11', 'q1');
    expect(defendsEvidence({ ...p('governador-11', 'governador', 1), defends: [e.id] }, [e, ev('governador-22', 'q1')])).toEqual([e]);
  });
});

describe('entities', () => {
  const weights = { record: 0.8, platform: 0.2 };
  const evidence = [ev('governador-11', 'q1'), ev('governador-27', 'q1'), ev('deputado_federal-1111', 'q1'), ev('PP', 'q1', { subject: { type: 'list', id: 'PP' } })];

  it('builds politicians from majoritarian candidates with evidence, without withdrawn ones', () => {
    expect(buildPoliticians(candidates, evidence, weights).map((x) => x.id)).toEqual(['governador-11']);
  });

  it('builds parties from list orientations and countries from stances', () => {
    expect(buildParties(evidence, buildCatalog(candidates), weights).map((x) => x.id)).toEqual(['list:PP']);
    expect(buildCountries([]).length).toBe(0);
  });

  it('limits the chart to profiled politicians when there are profiles', () => {
    const pols = buildPoliticians([...candidates, cand('governador-80')], [...evidence, ev('governador-80', 'q1')], weights);
    expect(chartPoliticians(pols, [p('governador-80', 'governador', 1)]).map((x) => x.id)).toEqual(['governador-80']);
    expect(chartPoliticians(pols, []).length).toBe(2);
  });
});

describe('compact profile helpers', () => {
  const claim = (text: string) => ({ text, support: text, source: { url: 'u', accessed: 'a', label: 'l' }, checkId: text });

  it('uses the first presents claim as the vibe line and counts the rest per section', () => {
    const prof = { ...p('governador-11', 'governador', 1), presents: [claim('Slogan'), claim('Coligação')], experience: [claim('a')] };
    expect(vibeLine(prof)?.text).toBe('Slogan');
    expect(sectionCounts(prof, [])).toEqual({ presents: 1, experience: 1, proposals: 0, defends: 0, controversies: 0 });
    expect(firstFilledSection(sectionCounts(prof, []))).toBe('experience');
    expect(vibeLine(p('governador-22', 'governador', null))).toBeNull();
  });

  it('shows 3 items and counts what is hidden until expanded', () => {
    expect(visibleSlice([1, 2, 3, 4, 5], false)).toEqual({ shown: [1, 2, 3], hidden: 2 });
    expect(visibleSlice([1, 2, 3, 4, 5], true)).toEqual({ shown: [1, 2, 3, 4, 5], hidden: 0 });
  });
});
