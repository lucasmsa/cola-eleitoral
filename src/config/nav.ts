import type { Screen } from '@/stores/screen';
import type { Turno } from '@/stores/turno';

export type NavAction = 'onHome' | 'onResults' | 'onReview' | 'onCola' | 'onRound2' | 'onRound1' | 'onCola2';

export interface NavLink {
  key: Screen['name'];
  label: string;
  action: NavAction;
  wideOnly?: boolean;
}

export const NAV_BY_TURNO: Record<Turno, NavLink[]> = {
  1: [
    { key: 'home', label: 'Início', action: 'onHome', wideOnly: true },
    { key: 'round1', label: 'Como foi', action: 'onRound1' },
    { key: 'results', label: 'Resultado', action: 'onResults' },
    { key: 'review', label: 'Quiz', action: 'onReview' },
    { key: 'cola', label: 'Cola', action: 'onCola' },
  ],
  2: [
    { key: 'home', label: 'Início', action: 'onHome', wideOnly: true },
    { key: 'round2', label: 'Comparar', action: 'onRound2' },
    { key: 'cola2', label: 'Cola', action: 'onCola2' },
  ],
};
