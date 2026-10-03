import { OFFICE_BY_ID } from '@/config/election';
import type { Candidate, CountryStance, Evidence, Office, Profile } from '@/data/schema';
import { countryPositions, subjectPositions, type AlignedEntity } from './alignment';
import type { Weights } from './score';
import type { Catalog } from './subjects';
import { titleCase } from './text';

const MAJORITARIAN = new Set<Office>(['presidente', 'governador', 'senador']);

export function buildPoliticians(candidates: Candidate[], evidence: Evidence[], weights: Weights): AlignedEntity[] {
  const withEvidence = new Set(evidence.filter((e) => e.subject.type === 'candidate').map((e) => e.subject.id));
  return candidates
    .filter((c) => MAJORITARIAN.has(c.office) && !c.withdrawn && withEvidence.has(c.id))
    .map((c) => ({
      id: c.id,
      label: titleCase(c.ballotName),
      detail: `${OFFICE_BY_ID[c.office].label}, ${c.party}`,
      kind: 'politico' as const,
      positions: subjectPositions(evidence, { type: 'candidate', id: c.id }, weights),
    }));
}

export function buildParties(evidence: Evidence[], catalog: Catalog, weights: Weights): AlignedEntity[] {
  const ids = [...new Set(evidence.filter((e) => e.subject.type === 'list').map((e) => e.subject.id))];
  return ids.map((id) => ({
    id: `list:${id}`,
    label: catalog.listNames.get(id) ?? id,
    detail: 'Orientação da liderança na Câmara',
    kind: 'partido' as const,
    positions: subjectPositions(evidence, { type: 'list', id }, weights),
  }));
}

export function buildCountries(stances: CountryStance[]): AlignedEntity[] {
  const names = [...new Set(stances.map((s) => s.country))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
  return names.map((name) => ({
    id: `pais:${name}`,
    label: name,
    detail: 'Lei ou política em vigor',
    kind: 'pais' as const,
    positions: countryPositions(stances, name),
  }));
}

/** The chart shows the profiled (top-polling) politicians when profiles exist, otherwise everyone with data. */
export function chartPoliticians(politicians: AlignedEntity[], profiles: Profile[]): AlignedEntity[] {
  const profiled = new Set(profiles.filter((p) => MAJORITARIAN.has(p.office)).map((p) => p.candidateId));
  if (profiled.size === 0) return politicians;
  return politicians.filter((p) => profiled.has(p.id));
}
