import type { ColaSlot } from '@/config/election';
import type { Candidate, Office } from '@/data/schema';

export type ColaEntry = { kind: 'number'; digits: string } | { kind: 'branco' };

export type SlotLookup =
  | { status: 'empty' }
  | { status: 'incomplete' }
  | { status: 'branco' }
  | { status: 'candidate'; candidate: Candidate }
  | { status: 'legenda'; partyNumber: string; party: string }
  | { status: 'not-found' };

export function partyNumbers(office: Office, candidates: Candidate[]): Map<string, string> {
  const map = new Map<string, string>();
  for (const c of candidates) {
    if (c.office === office) map.set(c.number.slice(0, 2), c.party);
  }
  return map;
}

export function sanitizeDigits(raw: string, max: number): string {
  return raw.replace(/\D/g, '').slice(0, max);
}

export function lookupSlot(slot: ColaSlot, entry: ColaEntry | undefined, candidates: Candidate[]): SlotLookup {
  if (!entry) return { status: 'empty' };
  if (entry.kind === 'branco') return { status: 'branco' };
  const digits = entry.digits;
  if (digits.length === 0) return { status: 'empty' };
  if (digits.length === slot.digits) {
    const candidate = candidates.find((c) => c.office === slot.office && c.number === digits);
    return candidate ? { status: 'candidate', candidate } : { status: 'not-found' };
  }
  if (slot.allowsLegenda && digits.length === 2) {
    const party = partyNumbers(slot.office, candidates).get(digits);
    return party ? { status: 'legenda', partyNumber: digits, party } : { status: 'not-found' };
  }
  return { status: 'incomplete' };
}

export function listParties(listId: string, office: Office, candidates: Candidate[]): { number: string; party: string }[] {
  const seen = new Map<string, string>();
  for (const c of candidates) {
    if (c.office === office && c.list === listId) seen.set(c.number.slice(0, 2), c.party);
  }
  return [...seen.entries()].map(([number, party]) => ({ number, party })).sort((a, b) => a.number.localeCompare(b.number));
}
