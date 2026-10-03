import type { Axis } from '@/data/schema';
import type { EntityKind } from '@/lib/alignment';

export const AXIS_LABELS: Record<Axis, { name: string; negative: string; positive: string }> = {
  economico: { name: 'Eixo econômico', negative: 'mais Estado', positive: 'mais mercado' },
  social: { name: 'Eixo de costumes', negative: 'progressista', positive: 'conservador' },
};

export function directionLabel(axis: Axis, direction: 1 | -1): string {
  const pole = direction === 1 ? AXIS_LABELS[axis].positive : AXIS_LABELS[axis].negative;
  return `Concordar puxa para ${pole}`;
}

export const KIND_LABELS: Record<EntityKind, string> = {
  politico: 'Políticos',
  partido: 'Partidos e federações',
  pais: 'Países',
};
