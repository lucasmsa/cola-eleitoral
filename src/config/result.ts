import type { Office } from '@/data/schema';
import { OFFICES } from './election';

export type ResultStep = 'alinhamento' | Office;

export interface ResultStepConfig {
  id: ResultStep;
  label: string;
}

export const RESULT_STEPS: ResultStepConfig[] = [
  { id: 'alinhamento', label: 'Alinhamento' },
  ...OFFICES.map((o) => ({ id: o.id, label: o.id === 'senador' ? 'Senado (2 votos)' : o.label })),
];
