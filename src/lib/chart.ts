import type { AxisAssignment } from '@/data/schema';
import { placeOnAxes, toUnit, type EntityKind, type Placement, type PositionMap } from './alignment';
import { estimateWidth, layoutLabels, type Box } from './chartLabels';

export const CHART = { size: 640, pad: 70 } as const;

export type DotKind = EntityKind | 'voce';

const S = CHART.size;
const P = CHART.pad;
/** Where the four pole labels are drawn outside the plot box; dot labels must not cover them. */
export const POLE_LABEL_BOXES: Box[] = [
  { x: P, y: S - P + 56, w: 130, h: 24 },
  { x: S - P - 150, y: S - P + 56, w: 150, h: 24 },
  { x: S / 2 - 70, y: S - P + 16, w: 140, h: 24 },
  { x: S / 2 - 70, y: P - 36, w: 140, h: 24 },
];

export interface Dot {
  id: string;
  label: string;
  detail: string;
  kind: DotKind;
  placement: Placement;
  cx: number;
  cy: number;
  labelDy: number;
  labelSide: 'left' | 'right';
  portrait?: string | null;
}

export interface Plottable {
  portrait?: string | null;
  id: string;
  label: string;
  detail: string;
  kind: DotKind;
  positions: PositionMap;
}

export function plotDots(items: Plottable[], axes: AxisAssignment[]): { dots: Dot[]; hidden: Plottable[] } {
  const inner = CHART.size - CHART.pad * 2;
  const placed = items.map((item) => {
    const placement = placeOnAxes(item.positions, axes);
    return {
      ...item,
      placement,
      cx: CHART.pad + toUnit(placement.x.value) * inner,
      cy: CHART.pad + (1 - toUnit(placement.y.value)) * inner,
    };
  });
  const visible = placed.filter((p) => p.placement.visible);
  const labels = layoutLabels(
    visible.map((v) => ({ id: v.id, cx: v.cx, cy: v.cy, width: estimateWidth(v.label) })),
    { min: 4, max: CHART.size - 4, top: CHART.pad - 6, bottom: CHART.size - CHART.pad + 10 },
    POLE_LABEL_BOXES,
  );
  const byId = new Map(labels.map((l) => [l.id, l]));
  return {
    dots: visible.map(({ positions: _positions, ...v }) => ({
      ...v,
      labelSide: byId.get(v.id)?.side ?? 'right',
      labelDy: byId.get(v.id)?.dy ?? 0,
    })),
    hidden: placed.filter((p) => !p.placement.visible),
  };
}
