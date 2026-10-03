import { COLA_SLOTS, type ColaSlot, type ColaSlotId } from '@/config/election';
import { candidates } from '@/data';
import { lookupSlot, sanitizeDigits, type ColaEntry, type SlotLookup } from '@/lib/cola';
import { useAnswersStore } from '@/stores/answers';
import { useNav } from './useNav';

export interface ColaSlotView {
  slot: ColaSlot;
  index: number;
  entry: ColaEntry | undefined;
  digits: string;
  lookup: SlotLookup;
}

export function slotViews(cola: Partial<Record<ColaSlotId, ColaEntry>>): ColaSlotView[] {
  return COLA_SLOTS.map((slot, index) => {
    const entry = cola[slot.id];
    return {
      slot,
      index,
      entry,
      digits: entry?.kind === 'number' ? entry.digits : '',
      lookup: lookupSlot(slot, entry, candidates),
    };
  });
}

export function useCola() {
  const cola = useAnswersStore((s) => s.cola);
  const setCola = useAnswersStore((s) => s.setCola);
  const nav = useNav();
  const views = slotViews(cola);
  const s1 = cola.senador_1;
  const s2 = cola.senador_2;
  const sameSenator = s1?.kind === 'number' && s2?.kind === 'number' && s1.digits.length === 3 && s1.digits === s2.digits;

  return {
    views,
    sameSenator,
    filled: views.filter((v) => v.lookup.status !== 'empty').length,
    typeDigits: (slot: ColaSlot, raw: string) => {
      const digits = sanitizeDigits(raw, slot.digits);
      setCola(slot.id, digits ? { kind: 'number', digits } : null);
    },
    setBranco: (slot: ColaSlot) => setCola(slot.id, { kind: 'branco' }),
    clear: (slot: ColaSlot) => setCola(slot.id, null),
    print: () => window.print(),
    openResults: nav.goResults,
  };
}
