import { brDate } from './text';

const STAMP = /(\d{2})\/(\d{2})\/(\d{4})(?:\s+às)?\s+(\d{2}):(\d{2})/;

function stampOf(text: string): string | null {
  const m = STAMP.exec(text);
  return m ? `${m[1]}/${m[2]}/${m[3]} ${m[4]}:${m[5]}` : null;
}

function sortKey(stamp: string): string {
  const [date, time] = stamp.split(' ') as [string, string];
  const [d, m, y] = date.split('/');
  return `${y}${m}${d}${time}`;
}

export function stampsIn(value: unknown): string[] {
  const found: string[] = [];
  const visit = (node: unknown, key: string) => {
    if (typeof node === 'string') {
      if (key === 'generated' || node.includes('gerado em')) {
        const stamp = stampOf(node);
        if (stamp) found.push(stamp);
      }
      return;
    }
    if (Array.isArray(node)) node.forEach((child) => visit(child, key));
    else if (node && typeof node === 'object') Object.entries(node).forEach(([k, child]) => visit(child, k));
  };
  visit(value, '');
  return found;
}

export function newestStamp(stamps: string[]): string | null {
  if (stamps.length === 0) return null;
  return stamps.reduce((a, b) => (sortKey(b) > sortKey(a) ? b : a));
}

interface FreshnessInput {
  candidates: unknown;
  results: unknown[];
  builtAt: string;
  polls: { office: string; institute: string; fieldStart: string; fieldEnd: string }[];
  officeLabel: (office: string) => string;
}

export interface Freshness {
  candidatos: string | null;
  resultados: string | null;
  evidencias: string;
  pesquisas: { office: string; institute: string; field: string }[];
}

export function dataFreshness(input: FreshnessInput): Freshness {
  return {
    candidatos: newestStamp(stampsIn(input.candidates)),
    resultados: newestStamp(stampsIn(input.results)),
    evidencias: brDate(input.builtAt),
    pesquisas: input.polls.map((p) => ({
      office: input.officeLabel(p.office),
      institute: p.institute,
      field: `${brDate(p.fieldStart)} a ${brDate(p.fieldEnd)}`,
    })),
  };
}
