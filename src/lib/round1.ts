import { COLA_SLOTS, type ColaSlotId } from '@/config/election';
import type { MajoritarianResult, ProportionalResult, ResultCandidate, Round1 } from '@/data/schema';
import type { ColaEntry } from './cola';

export function formatInt(n: number): string {
  return n.toLocaleString('pt-BR');
}

export interface BarRow extends ResultCandidate {
  width: number;
  highlight: boolean;
}

export function barRows(section: MajoritarianResult, highlight: string[] = []): BarRow[] {
  const sorted = [...section.candidates].sort((a, b) => b.votes - a.votes);
  const top = sorted[0]?.pct || 1;
  return sorted.map((c) => ({ ...c, width: c.pct / top, highlight: highlight.includes(c.candidateId) }));
}

export interface ListGroup {
  list: string;
  parties: string;
  seats: number;
  people: ProportionalResult['elected'];
}

export function electedByList(section: ProportionalResult): ListGroup[] {
  return section.seats.map((s) => ({
    list: s.list,
    parties: s.parties,
    seats: s.seats,
    people: section.elected.filter((e) => e.list === s.list).sort((a, b) => b.votes - a.votes),
  }));
}

export type PickOutcome = 'eleito' | 'segundo-turno' | 'suplente' | 'nao-eleito' | 'legenda' | 'branco' | 'nao-encontrado';

export interface PickRow {
  slot: ColaSlotId;
  label: string;
  outcome: PickOutcome;
  name: string | null;
  detail: string | null;
}

function sectionFor(slot: ColaSlotId, r: Round1): MajoritarianResult | ProportionalResult {
  switch (slot) {
    case 'presidente':
      return r.presidente.br;
    case 'governador':
      return r.governador;
    case 'senador_1':
    case 'senador_2':
      return r.senador;
    case 'deputado_federal':
      return r.deputadoFederal;
    case 'deputado_estadual':
      return r.deputadoEstadual;
  }
}

function candidateOutcome(c: ResultCandidate): PickOutcome {
  if (c.elected) return 'eleito';
  if (c.status === '2º turno') return 'segundo-turno';
  if (c.status === 'Suplente') return 'suplente';
  return 'nao-eleito';
}

function legendaDetail(digits: string, section: ProportionalResult): string | null {
  const member = section.elected.find((e) => e.number.startsWith(digits));
  const seats = section.seats.find((s) => s.list === member?.list) ?? section.seats.find((s) => s.parties.includes(digits));
  if (!seats) return null;
  return `${seats.list}: ${seats.seats} ${seats.seats === 1 ? 'vaga' : 'vagas'}`;
}

export function pickOutcomes(cola: Partial<Record<ColaSlotId, ColaEntry>>, r: Round1): PickRow[] {
  const rows: PickRow[] = [];
  for (const slot of COLA_SLOTS) {
    const entry = cola[slot.id];
    if (!entry) continue;
    if (entry.kind === 'branco') {
      rows.push({ slot: slot.id, label: slot.label, outcome: 'branco', name: null, detail: null });
      continue;
    }
    const section = sectionFor(slot.id, r);
    const isLegenda = slot.allowsLegenda && entry.digits.length === 2;
    if (isLegenda && 'seats' in section) {
      rows.push({ slot: slot.id, label: slot.label, outcome: 'legenda', name: null, detail: legendaDetail(entry.digits, section) });
      continue;
    }
    const found = section.candidates.find((c) => c.number === entry.digits);
    if (!found) {
      rows.push({ slot: slot.id, label: slot.label, outcome: 'nao-encontrado', name: null, detail: entry.digits });
      continue;
    }
    rows.push({ slot: slot.id, label: slot.label, outcome: candidateOutcome(found), name: found.ballotName, detail: found.pctLabel ? `${found.pctLabel}%` : null });
  }
  return rows;
}
