import { COPY } from '@/config/copy';
import type { SlotLookup } from './cola';
import { titleCase } from './text';

export type ColaStatusKind = 'ok' | 'warn' | 'idle';

export function colaStatus(lookup: SlotLookup, digits: number): { kind: ColaStatusKind; text: string } {
  switch (lookup.status) {
    case 'candidate': {
      const name = `${titleCase(lookup.candidate.ballotName)}, ${lookup.candidate.party}`;
      const notice = lookup.candidate.notice;
      return notice ? { kind: 'warn', text: `${name}. ${notice.text}` } : { kind: 'ok', text: name };
    }
    case 'legenda':
      return { kind: 'ok', text: COPY.cola.legenda(lookup.party) };
    case 'branco':
      return { kind: 'ok', text: COPY.cola.brancoLabel };
    case 'not-found':
      return { kind: 'warn', text: COPY.cola.notFound };
    case 'incomplete':
      return { kind: 'warn', text: COPY.cola.incomplete(digits) };
    default:
      return { kind: 'idle', text: COPY.cola.empty };
  }
}
