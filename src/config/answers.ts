import type { Importance, Stance } from '@/lib/score';

export const STANCES: { value: Stance; label: string }[] = [
  { value: -1, label: 'Discordo totalmente' },
  { value: -0.5, label: 'Discordo' },
  { value: 0, label: 'Neutro' },
  { value: 0.5, label: 'Concordo' },
  { value: 1, label: 'Concordo totalmente' },
];

export const IMPORTANCES: { value: Importance; label: string }[] = [
  { value: 0.5, label: 'Quase nada' },
  { value: 1, label: 'Um pouco' },
  { value: 2, label: 'Muito' },
];

export const DEFAULT_IMPORTANCE: Importance = 1;
export const DEFAULT_WEIGHTS = { record: 0.8, platform: 0.2 };

export function importanceLabel(value: Importance): string {
  return IMPORTANCES.find((i) => i.value === value)?.label ?? '';
}
