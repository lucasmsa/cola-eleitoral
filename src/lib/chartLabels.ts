export interface LabelRequest {
  id: string;
  cx: number;
  cy: number;
  width: number;
}

export interface PlacedLabel {
  id: string;
  side: 'left' | 'right';
  dy: number;
}

export interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
}

const LINE = 16;
const GAP = 12;
const DOT = 7;

function hit(a: Box, b: Box): boolean {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

function labelBox(r: LabelRequest, side: 'left' | 'right', dy: number): Box {
  const x = side === 'right' ? r.cx + GAP : r.cx - GAP - r.width;
  return { x, y: r.cy - LINE / 2 + dy, w: r.width, h: LINE };
}

/** Tries right, left, then one line down/up on each side; labels avoid other labels, other dots and the drawing's edges. */
export function layoutLabels(
  requests: LabelRequest[],
  bounds: { min: number; max: number; top?: number; bottom?: number },
  obstacles: Box[] = [],
): PlacedLabel[] {
  const dots: (Box & { id: string })[] = requests.map((r) => ({ id: r.id, x: r.cx - DOT, y: r.cy - DOT, w: DOT * 2, h: DOT * 2 }));
  const taken: Box[] = [];
  const out: PlacedLabel[] = [];
  const candidates: ['left' | 'right', number][] = [
    ['right', 0],
    ['left', 0],
    ['right', LINE],
    ['left', LINE],
    ['right', -LINE],
    ['left', -LINE],
    ['right', 2 * LINE],
    ['left', 2 * LINE],
    ['right', -2 * LINE],
    ['left', -2 * LINE],
  ];
  for (const r of [...requests].sort((a, b) => a.cy - b.cy || a.cx - b.cx)) {
    const fits = ([side, dy]: ['left' | 'right', number]) => {
      const box = labelBox(r, side, dy);
      if (box.x < bounds.min || box.x + box.w > bounds.max) return false;
      if (bounds.top !== undefined && box.y < bounds.top) return false;
      if (bounds.bottom !== undefined && box.y + box.h > bounds.bottom) return false;
      if (taken.some((t) => hit(t, box)) || obstacles.some((o) => hit(o, box))) return false;
      return !dots.some((d) => d.id !== r.id && hit(d, box));
    };
    const [side, dy] = candidates.find(fits) ?? (r.cx > (bounds.min + bounds.max) / 2 ? ['left', 0] : ['right', 0]);
    taken.push(labelBox(r, side, dy));
    out.push({ id: r.id, side, dy });
  }
  return out;
}

export function estimateWidth(label: string, charWidth = 8.6): number {
  return label.length * charWidth;
}
