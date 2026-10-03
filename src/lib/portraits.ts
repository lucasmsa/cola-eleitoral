import type { Portrait } from '@/data/schema';

export type PortraitIndex = Map<string, Portrait>;

export function indexPortraits(portraits: Portrait[]): PortraitIndex {
  return new Map(portraits.map((p) => [p.candidateId, p]));
}

const SKIP = new Set(['de', 'da', 'do', 'das', 'dos', 'e', 'dr.', 'dr', 'dra.', 'escritor', 'veterinário', 'major', 'sargento', 'cabo', 'pastor']);

/** Two letters for the initials stamp: first and last meaningful words of the ballot name. */
export function initials(name: string): string {
  const words = name
    .toLocaleLowerCase('pt-BR')
    .split(/\s+/)
    .filter((w) => w && !SKIP.has(w));
  if (words.length === 0) return '?';
  const first = words[0]!.charAt(0);
  const last = words.length > 1 ? words[words.length - 1]!.charAt(0) : '';
  return (first + last).toLocaleUpperCase('pt-BR');
}
