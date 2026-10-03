import { OFFICES } from '@/config/election';
import { LIST_LABELS } from '@/config/lists';
import type { Candidate, Evidence, Office } from '@/data/schema';
import { titleCase } from './text';

export interface SubjectInfo {
  type: 'candidate' | 'list';
  id: string;
  name: string;
  number: string | null;
  listName: string;
  office: Office | null;
  candidate: Candidate | null;
}

export interface Catalog {
  candidates: Map<string, Candidate>;
  listNames: Map<string, string>;
}

export function buildCatalog(candidates: Candidate[]): Catalog {
  const listNames = new Map<string, string>();
  for (const c of candidates) listNames.set(c.list, LIST_LABELS[c.list] ?? c.listName);
  return { candidates: new Map(candidates.map((c) => [c.id, c])), listNames };
}

export function describeSubject(catalog: Catalog, subject: Evidence['subject']): SubjectInfo {
  if (subject.type === 'list') {
    const listName = catalog.listNames.get(subject.id) ?? subject.id;
    return { type: 'list', id: subject.id, name: listName, number: null, listName, office: null, candidate: null };
  }
  const c = catalog.candidates.get(subject.id);
  if (!c) {
    return { type: 'candidate', id: subject.id, name: subject.id, number: null, listName: '', office: null, candidate: null };
  }
  return {
    type: 'candidate',
    id: c.id,
    name: titleCase(c.ballotName),
    number: c.number,
    listName: catalog.listNames.get(c.list) ?? c.listName,
    office: c.office,
    candidate: c,
  };
}

export type EvidenceBadge = 'Votou' | 'Orientou' | 'Sancionou ou vetou' | 'Declarou';

export function evidenceBadge(e: Evidence): EvidenceBadge {
  if (e.kind === 'platform') return 'Declarou';
  if (e.subject.type === 'list') return 'Orientou';
  if (/^(Sancion|Vet)/.test(e.detail)) return 'Sancionou ou vetou';
  return 'Votou';
}

export interface SubjectEvidence {
  subject: SubjectInfo;
  evidence: Evidence[];
}

export interface EvidenceGroup {
  key: string;
  label: string;
  items: SubjectEvidence[];
}

const LIST_GROUP = 'Partidos e federações (orientação na Câmara)';

export function groupEvidence(catalog: Catalog, items: Evidence[]): EvidenceGroup[] {
  const groups: EvidenceGroup[] = OFFICES.map((o) => ({ key: o.id, label: o.label, items: [] }));
  const lists: EvidenceGroup = { key: 'list', label: LIST_GROUP, items: [] };
  for (const e of items) {
    const subject = describeSubject(catalog, e.subject);
    const group = subject.type === 'list' ? lists : groups.find((g) => g.key === subject.office);
    if (!group) continue;
    const entry = group.items.find((i) => i.subject.type === subject.type && i.subject.id === subject.id);
    if (entry) entry.evidence.push(e);
    else group.items.push({ subject, evidence: [e] });
  }
  for (const g of [...groups, lists]) g.items.sort((a, b) => a.subject.name.localeCompare(b.subject.name, 'pt-BR'));
  return [...groups, lists].filter((g) => g.items.length > 0);
}
