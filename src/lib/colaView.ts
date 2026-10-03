import type { SlotLookup } from './cola';
import { titleCase } from './text';

export function colaRowName(lookup: SlotLookup): string {
  switch (lookup.status) {
    case 'candidate':
      return titleCase(lookup.candidate.ballotName);
    case 'legenda':
      return `legenda ${lookup.party}`;
    case 'branco':
      return 'BRANCO';
    default:
      return '';
  }
}
